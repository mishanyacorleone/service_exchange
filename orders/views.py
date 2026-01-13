from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import redirect_to_login
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.core.exceptions import PermissionDenied
from .models import Order, Bid
from .forms import BidForm, OrderForm
# Create your views here.


def order_list(request):
    orders = Order.objects.filter(status='open').select_related('customer')
    return render(request, 'orders/order_list.html', {'orders': orders})


def executor_list(request):
    executors = User.objects.filter(profile__role='executor').select_related('profile')
    return render(request, 'orders/executor_list.html', {'executors': executors})


@login_required
def my_orders(request):
    if request.user.profile.role != 'customer':
        raise PermissionDenied

    customer_orders = Order.objects.filter(customer=request.user)
    return render(request, 'orders/my_orders.html', {'customer_orders': customer_orders})


@login_required
def my_assigned_orders(request):
    if request.user.profile.role != 'executor':
        raise PermissionDenied

    assigned_orders = Order.objects.filter(assigned_executor=request.user).select_related('customer')
    return render(request, 'orders/my_assigned_orders.html', {'assigned_orders': assigned_orders})


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    is_customer = request.user.is_authenticated and request.user == order.customer
    is_executor = request.user.is_authenticated and request.user.profile.role == 'executor'

    is_assigned_executor = request.user.is_authenticated and request.user == order.assigned_executor

    bids = order.bids.all().select_related('executor__profile')

    user_can_bid = False
    bid_form = None
    if is_executor:
        user_can_bid = not Bid.objects.filter(order=order, executor=request.user).exists()

        if request.method == 'POST' and user_can_bid:
            bid_form = BidForm(request.POST)
            if bid_form.is_valid():
                bid = bid_form.save(commit=False)
                bid.order = order
                bid.executor = request.user
                bid.save()
                return HttpResponseRedirect(request.path)
        else:
            bid_form = BidForm() if user_can_bid else None

    if request.method == 'POST' and is_customer and 'assign_executor' in request.POST:
        executor_id = request.POST.get('executor_id')
        if executor_id:
            try:
                selected_executor = User.objects.get(id=executor_id, profile__role='executor')
                if Bid.objects.filter(order=order, executor=selected_executor).exists():
                    order.assigned_executor = selected_executor
                    order.status = 'in_progress'
                    order.save()
                    return HttpResponseRedirect(request.path)
                else:
                    pass
            except User.DoesNotExist:
                pass

    if request.method == 'POST' and is_customer and 'change_status' in request.POST:
        new_status = request.POST.get('new_status')
        allowed_statuses = [choice[0] for choice in order.get_allowed_status_transitions()]
        if new_status in allowed_statuses:
            order.status = new_status
            if new_status in ['open', 'completed', 'cancelled']:
                order.assigned_executor = None
            order.save()
            return HttpResponseRedirect(request.path)

    if request.method == 'POST' and is_customer and 'unassign_executor' in request.POST:
        order.assigned_executor = None
        order.status = 'open'
        order.save()
        return HttpResponseRedirect(request.path)

    context = {
        'order': order,
        'bids': bids,
        'is_customer': is_customer,
        'is_executor': is_executor,
        'is_assigned_executor': is_assigned_executor,
        'user_can_bid': user_can_bid,
        'bid_form': bid_form,
        'bidders_for_selection': bids.values_list('executor__id', 'executor__username') if is_customer else [],
        'allowed_status_transitions': order.get_allowed_status_transitions() if is_customer or is_assigned_executor else [],
    }
    print(order.status)
    print(order.get_allowed_status_transitions())

    return render(request, 'orders/order_detail.html', context)


def create_order(request):
    if not request.user.is_authenticated:
        return redirect_to_login(request.get_full_path())

    if request.user.profile.role != 'customer':
        raise PermissionDenied

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.customer = request.user
            order.save()
            return redirect('my_orders')

    else:
        form = OrderForm()

    return render(request, 'orders/create_order.html', {'form': form})


@login_required
def edit_order(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.user != order.customer:
        raise PermissionDenied

    if request.method == 'POST':
        form = OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('order_detail', order_id=order.id)

    else:
        form = OrderForm(instance=order)

    return render(request, 'orders/edit_order.html', {'form': form, 'order': order})
