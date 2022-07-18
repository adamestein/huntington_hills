def median_value(queryset, term):
    count = queryset.count()
    values = queryset.values_list(term, flat=True).order_by(term)
    return values[int(round(count/2))] if count % 2 == 1 else sum(values[count/2-1:count/2+1])/2.0
