
from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from django.core.mail import send_mail
from django.conf import settings
from ipaddress import IPv4Network, IPv4Address
from .forms import SubnetCalculatorForm



def calculate_subnets(network, host_requirements):
    try:
        base_network = IPv4Network(network, strict=False)
        host_requirements = sorted([int(x) for x in host_requirements], reverse=True)

        subnets = []
        remaining_network = base_network

        for hosts in host_requirements:
            prefix = 32 - (hosts + 1).bit_length()
            for subnet in remaining_network.subnets(new_prefix=prefix):
                if subnet.num_addresses - 2 >= hosts:
                    subnets.append({
                        'subnet': subnet.with_prefixlen,
                        'network_address': subnet.network_address,
                        'broadcast_address': subnet.broadcast_address,
                        'subnet_mask': subnet.netmask,
                        'first_host': subnet.network_address + 1,
                        'last_host': subnet.broadcast_address - 1,
                        'usable_hosts': subnet.num_addresses - 2
                    })
                    remaining_network = list(remaining_network.address_exclude(subnet))[0]
                    break

        return subnets
    except Exception as e:
        raise ValueError(f"Error calculating subnets: {str(e)}")


def subnet_calculator(request):
    if request.method == 'POST':
        form = SubnetCalculatorForm(request.POST)
        if form.is_valid():
            network = form.cleaned_data['network']
            host_requirements = form.cleaned_data['host_requirements'].split(',')
            email = form.cleaned_data['email']

            try:
                subnets = calculate_subnets(network, host_requirements)

                # Prepare email content if email is provided
                if email:
                    email_content = f"Subnet Calculation Results for {network}\n\n"
                    for i, subnet in enumerate(subnets, 1):
                        email_content += (
                            f"Subnet {i}:\n"
                            f"  Subnet: {subnet['subnet']}\n"
                            f"  Network Address: {subnet['network_address']}\n"
                            f"  Broadcast Address: {subnet['broadcast_address']}\n"
                            f"  Subnet Mask: {subnet['subnet_mask']}\n"
                            f"  First Usable Host: {subnet['first_host']}\n"
                            f"  Last Usable Host: {subnet['last_host']}\n"
                            f"  Usable Hosts: {subnet['usable_hosts']}\n\n"
                        )

                    send_mail(
                        'Your IPv4 Subnet Calculation Results',
                        email_content,
                        settings.EMAIL_HOST_USER,
                        [email],
                        fail_silently=False,
                    )

                return render(request, 'calculator/results.html', {
                    'subnets': subnets,
                    'network': network,
                    'email_sent': bool(email)
                })

            except ValueError as e:
                form.add_error(None, str(e))
    else:
        form = SubnetCalculatorForm()

    return render(request, 'calculator/index.html', {'form': form})