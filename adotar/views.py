from django.shortcuts import render, redirect
from divulgar .models import Pet, Raca
from django.contrib.messages import constants
from django.contrib import messages
from .models import PedidoAdocao, Pet
from datetime import datetime
from divulgar.models import Pet
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required

@login_required
def  listar_pets(request):
    if request.method == "GET":
        pets = Pet.objects.filter(status='P')
        racas = Raca.objects.all()

        cidade = request.GET.get('cidade')
        raca_filter = request.GET.get('raca')

        if cidade:
            pets = pets.filter(cidade__icontains=cidade)

        if raca_filter:
            pets = pets.filter(raca__id=raca_filter)
            raca_filter = Raca.objects.get(id=raca_filter)

        return render(request, 'listar_pets.html',{'pets':pets,'racas':racas,'cidade':cidade, 'raca_filter':raca_filter})

@login_required
def pedido_adocao(request,id_pet):
    pet = Pet.objects.filter(id=id_pet).filter(status="P")
    peti = Pet.objects.get(id=id_pet) #pega os dados do dono do pet
    if not pet.exists():
        messages.add_message(request, constants.WARNING, 'Esse pet já foi adotado')
        return redirect('/adotar')
    
    pedido = PedidoAdocao(pet=pet.first(),
                          usuario=peti.usuario, #dados do dono do pet sendo enviados para o sistema                  
                          data=datetime.now())
    pedido.save()
    messages.add_message(request, constants.SUCCESS, 'Pedido de adoção realizado com sucesso')
    return redirect('/adotar')

@login_required
def processa_pedido_adocao(request, id_pedido):
    status = request.GET.get('status')
    pedido = PedidoAdocao.objects.get(id=id_pedido)
    pet_id = pedido.pet.id #id do pet pego pelo pedido
    pet = Pet.objects.get(id=pet_id)

    if status == "A":
        pedido.status = 'AP' #altera status do pedido para aprovado
        pet.status = "A" #altera o status do pet para adotado
        string = ''' Olá, sua adoção foi aprovada com sucesso'''
    elif status == "R":
        string = ''' Olá, sua adoção foi recusada'''
        pedido.status = 'R' 
        pet.status = "P"
    
    pet.save()
    pedido.save()

    email = send_mail(
        'Sua adoção foi processada',
        string,
        'flipeandre12@gmail.com',
        [pedido.usuario.email,]
    )

    messages.add_message(request, constants.SUCCESS, 'Pedido de adoção processado com sucesso')
    return redirect('/divulgar/ver_pedido_adocao')