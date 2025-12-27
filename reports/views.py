from django.shortcuts import render

# Create your views here.
class SalesReportView(LoginRequiredMixin, UserPassesTestMixin, View):
    def get(self, request):
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        
        if start_date and end_date:
            orders = LaundryOrder.objects.filter(
                registered_at__date__range=[start_date, end_date]
            )
            
            # Generate report data
            report_data = {
                'total_orders': orders.count(),
                'total_revenue': orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
                'average_order_value': orders.aggregate(Avg('total_amount'))['total_amount__avg'] or 0,
                'orders_by_status': orders.values('status').annotate(count=Count('id')),
                'top_items': OrderItem.objects.filter(
                    order__in=orders
                ).values('clothing_type__name').annotate(
                    total_quantity=Sum('quantity')
                ).order_by('-total_quantity')[:10]
            }
            
            if request.GET.get('export') == 'excel':
                return self.export_to_excel(report_data, start_date, end_date)
        
        return render(request, 'reports/sales_report.html', context)