from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect

from item.models import Item

from .forms import ConversationMessageForm
from .models import Conversation, ConversationMessage

@login_required
def new_conversation(request, item_pk):
    # Fetching a single object from the database based on primary key
    item = get_object_or_404(Item, pk=item_pk)

    # If you are the user that created this item redirect:
    if item.created_by == request.user:
        return redirect(' dashboard:index ')
    
    # Return all the conversations related to this item where the user is a member
    conversations = Conversation.objects.filter(item=item).filter(members__in=[request.user.id])

    # If there already is a conversation between you and the seller on this item redirect to that conversation
    if conversations:
        return redirect('conversation:detail', pk = conversations.first().id )

    if request.method == 'POST':
        form = ConversationMessageForm(request.POST)

        if form.is_valid():
            conversation = Conversation.objects.create(item = item)
            conversation.members.add(request.user)
            conversation.members.add(item.created_by)
            conversation.save()

            conversation_message = form.save(commit = False)
            conversation_message.conversation = conversation
            conversation_message.created_by = request.user
            conversation_message.save()

            return redirect('item:detail', pk=item_pk)
    else:
        form = ConversationMessageForm()

    return render(request, 'conversation/new.html', {
        'form': form
    })

@login_required
def inbox(request):
    conversations = Conversation.objects.filter(members__in=[request.user.id])

    return render(request, 'conversation/inbox.html', {
        'conversations': conversations
    })

@login_required
def detail(request, pk):
    conversation = Conversation.objects.filter(members__in=[request.user.id]).get(pk=pk)


    # must review this part. quite interesting.
    if request.method == 'POST':
        form = ConversationMessageForm(request.POST)

        if form.is_valid():
            conversation_message = form.save(commit = False)
            conversation_message.conversation = conversation
            conversation_message.created_by = request.user
            conversation_message.save()

            conversation.save()

            return redirect('conversation:detail', pk=pk)
    else:
        form = ConversationMessageForm()

    return render(request, 'conversation/detail.html', {
        'conversation': conversation,
        'form': form
    })