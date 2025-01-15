from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.http import Http404 

from django.contrib import messages

from .models import (
    ChatGroup,
    GroupMessage
)

from .forms import (
    ChatmessageCreateForm,
    NewGroupForm
)




class ChatView(LoginRequiredMixin, View): 
    template_name = 'a_rtchat/chat.html'

    def get_common_context(self, chatroom_name):
        chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
        chat_messages = GroupMessage.objects.prefetch_related('author').filter(group=chat_group)
        form = ChatmessageCreateForm()
        
        return {
            'form': form,
            'chat_messages': chat_messages,
            'chat_group': chat_group,
            'online_count': '0 online',
            'chat_group': chat_group
        }

    def get(self, request, chatroom_name="public-chat"):
        context = self.get_common_context(chatroom_name)
        other_user = None
        chat_group = context.get('chat_group')
        
        if chat_group.is_private:
            if request.user not in chat_group.members.all():
                raise Http404()
            for member in chat_group.members.all():
                if member != request.user:
                    other_user = member 
                    break
        
        if chat_group.groupchat_name:
            #Это нужно если другой пользовтаель будет присойденять к имменовоной группе чата мы его добавли 
            #дургой пользователь это тот каторый не создаел этот имменованный группой чат
            if request.user not in chat_group.members.all():
                chat_group.members.add(request.user)
        
        context.update({'other_user': other_user})
        context.update({"chatroom_name": chatroom_name})
        return render(request, self.template_name, context)

    def post(self, request):
        context = self.get_common_context()
        form = ChatmessageCreateForm(request.POST)
        
        if request.htmx:
            if form.is_valid():
                message = form.save(commit=False)
                message.author = request.user
                message.group = context['chat_group']
                message.save()
                
                # Обновляем контекст для нового сообщения
                context['message'] = message
                return render(request, 'a_rtchat/partials/chat_message_p.html', {'message': message})

        
        context['form'] = form
        return render(request, self.template_name, context)
    
    
class GetOrCreateChatRoom(LoginRequiredMixin, View):
    def get(self, request, username):
        if request.user.username == username:
            return redirect('home-chat:home')
        
        other_user = User.objects.get(username=username)
        my_chatrooms = ChatGroup.objects.filter(members=request.user, is_private=True)  
        
        if my_chatrooms.exists():
            for chatroom in my_chatrooms:
                if other_user in chatroom.members.all():
                    chatroom = chatroom
                    break
                else:
                    chatroom = ChatGroup.objects.create(
                        is_private=True
                    )
                    chatroom.members.add(other_user, request.user)
        else:
            chatroom = ChatGroup.objects.create(
                is_private=True
            )
            chatroom.members.add(other_user, request.user)
        
        
        return redirect('home-chat:chatroom', chatroom.group_name)



class CreateGroupChat(LoginRequiredMixin, View):
    def get(self, request):
        form = NewGroupForm()
        context = {'form': form}
        return render(request, 'a_rtchat/create_groupchat.html', context)
    def post(self, request):
        form = NewGroupForm(request.POST)
        if form.is_valid():
            new_groupchat = form.save(commit=False)
            new_groupchat.admin = request.user
            new_groupchat.save()
            new_groupchat.members.add(request.user)
            return redirect("home-chat:chatroom", new_groupchat.group_name)
        

class ChatRoomEditView(LoginRequiredMixin, View):
    def get(self, request, chatroom_name):
        chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
        if request.user != chat_group.admin:
            raise Http404()
        
        form = NewGroupForm(instance=chat_group)
        
        context = {
            "form": form,
            "chat_group": chat_group
        }
        return render(request, "a_rtchat/chatroom_edit.html", context)
    
    def post(self, request, chatroom_name):
        chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
        form = NewGroupForm(request.POST, instance=chat_group)
        
        if form.is_valid():
            form.save()
            
            remove_members = request.POST.getlist('remove_members')
            for member_id in remove_members:
                member = User.objects.get(id=member_id)
                chat_group.members.remove(member)
                
            return redirect("home-chat:chatroom", chatroom_name)
        
        
        
class ChatRoomDeleteView(LoginRequiredMixin, View):
    def get(self, request, chatroom_name):
        chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
        if request.user != chat_group.admin:
            raise Http404()
        
        context = {
            "chat_group": chat_group
        }
        return render(request, 'a_rtchat/chatroom_delete.html', context)
    
    def post(self, request, chatroom_name):
        chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
        chat_group.delete()
        messages.success(request, "Chatroom deleted")
        return redirect("home-chat:home")


class ChatRoomLeaveView(LoginRequiredMixin, View):
    def get(self, request, chatroom_name):
        chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
        if request.user not in chat_group.members.all():
            raise Http404()

        context = {"chat_group": chat_group}
        return render(request, "a_rtchat/chatroom_leave.html", context)
    
    def post(self, request, chatroom_name):
        chat_group = get_object_or_404(ChatGroup, group_name=chatroom_name)
        if request.user not in chat_group.members.all():
            raise Http404()

        chat_group.members.remove(request.user)
        messages.success(request, "You left the Chat")
        return redirect("home-chat:home")