from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Count, Q, Avg
from django.utils import timezone
from datetime import timedelta
from .models import Ticket
from .serializers import TicketSerializer
import openai
from django.conf import settings


class TicketListCreate(generics.ListCreateAPIView):
    queryset = Ticket.objects.all().order_by('-created_at')
    serializer_class = TicketSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filters
        category = self.request.query_params.get('category')
        priority = self.request.query_params.get('priority')
        status = self.request.query_params.get('status')
        search = self.request.query_params.get('search')
        
        if category:
            queryset = queryset.filter(user_category=category)
        if priority:
            queryset = queryset.filter(user_priority=priority)
        if status:
            queryset = queryset.filter(status=status)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | Q(description__icontains=search)
            )
        
        return queryset

class TicketDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer

# @api_view(['POST'])
# def classify_ticket(request):
#     # Temporary mock response - LLM integration later
#     description = request.data.get('description', '')
    
#     # Mock logic - replace with LLM later
#     if 'bill' in description.lower():
#         suggested_category = 'billing'
#         suggested_priority = 'high'
#     elif 'login' in description.lower():
#         suggested_category = 'account'
#         suggested_priority = 'medium'
#     else:
#         suggested_category = 'general'
#         suggested_priority = 'low'
    
#     return Response({
#         'suggested_category': suggested_category,
#         'suggested_priority': suggested_priority
#     })

@api_view(['POST'])
def classify_ticket(request):
    description = request.data.get('description', '')
    
    if not description:
        return Response({
            'suggested_category': '',
            'suggested_priority': ''
        })
    
    try:
        openai.api_key = settings.OPENAI_API_KEY
        
        prompt = f"""
        Given this support ticket description, classify it into:
        - Category: billing, technical, account, or general
        - Priority: low, medium, high, or critical
        
        Description: "{description}"
        
        Return ONLY JSON format: {{"category": "...", "priority": "..."}}
        """
        
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You classify support tickets. Return only JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
            max_tokens=50
        )
        
        result = eval(response.choices[0].message.content)  # Simple parse
        
        return Response({
            'suggested_category': result.get('category', 'general'),
            'suggested_priority': result.get('priority', 'low')
        })
        
    except Exception as e:
        # Fail gracefully - return empty suggestions
        return Response({
            'suggested_category': '',
            'suggested_priority': ''
        })

@api_view(['GET'])
def ticket_stats(request):
    total = Ticket.objects.count()
    open_tickets = Ticket.objects.filter(status='open').count()
    
    # Last 7 days average
    week_ago = timezone.now() - timedelta(days=7)
    tickets_last_week = Ticket.objects.filter(created_at__gte=week_ago).count()
    avg_per_day = round(tickets_last_week / 7, 1)
    
    # Priority breakdown
    priority_stats = Ticket.objects.values('user_priority').annotate(count=Count('id'))
    priority_breakdown = {item['user_priority']: item['count'] for item in priority_stats}
    
    # Category breakdown
    category_stats = Ticket.objects.values('user_category').annotate(count=Count('id'))
    category_breakdown = {item['user_category']: item['count'] for item in category_stats}
    
    return Response({
        'total_tickets': total,
        'open_tickets': open_tickets,
        'avg_tickets_per_day': avg_per_day,
        'priority_breakdown': priority_breakdown,
        'category_breakdown': category_breakdown,
    })
# Create your views here.
