from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, FormView, DetailView, TemplateView, ListView
from django.urls import reverse_lazy
from django.db.models import Count # いいねのカウント
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage # ページネーション機能

from django.core.mail import send_mail, EmailMessage # メール送信機能
from django.template.loader import get_template

from . models import Topic
from . models import Category
from . models import Comment
from . forms import TopicCreateForm, TopicForm, CommentModelForm, TopicModelForm

class TopicDetailView(DetailView):
    template_name = 'thread/detail_topic.html'
    model = Topic
    context_object_name = 'topic'

class TopicTemplateView(TemplateView):
    template_name = 'thread/detail_topic.html'
    
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['topic'] = get_object_or_404(Topic, id=self.kwargs.get('pk', ''))
        return ctx

# FormViewを使ったやり方
class TopicFormView(FormView):
    template_name = 'thread/create_topic.html'
    # 指定されたフォームを'form'という名前でコンテキストとして渡す
    form_class = TopicCreateForm        
    success_url = reverse_lazy('base:top')

    def form_valid(self, form):
        form.save()
        return super().form_valid(form) # 保存

# CreateViewを使ったやり方
class TopicCreateView_test(CreateView):
    template_name = 'thread/create_topic.html'
    form_class = TopicCreateForm
    model = Topic
    success_url = reverse_lazy('base:top')


# forms.ModelFormを使った場合の処理
def topic_create_test(request):
    template_name = 'thread/create_topic.html'
    ctx = {}
    if request.method == 'GET':
        ctx['form'] = TopicCreateForm()
        return render(request, template_name, ctx)
    
    if request.method == 'POST':
        topic_form = TopicCreateForm(request.POST)
        if topic_form.is_valid():
            topic_form.save()
            return redirect(reverse_lazy('base:top'))
        else:
            ctx['form'] = topic_form
            return render(request, template_name, ctx)

# forms.Formを使った場合の処理
def topic_create(request):
    template_name = 'thread/create_topic.html'
    ctx = {}
    if request.method == 'GET':
        form = TopicForm()
        ctx['form'] = form
        return render(request, template_name, ctx)
    
    if request.method == 'POST':
        topic_form = TopicForm(request.POST)
        if topic_form.is_valid():
            # topic_form.save()
            topic = Topic()
            cleaned_data = topic_form.cleaned_data
            topic.title = cleaned_data['title']
            topic.message = cleaned_data['message']
            topic.user_name = cleaned_data['user_name']
            topic.category = cleaned_data['category']
            topic.save()            
            return redirect(reverse_lazy('base:top'))
        else:
            ctx['form'] = topic_form
            return render(request, template_name, ctx)


# CreateViewの場合、保存はsuper().form_valid(form)のタイミングで行われる
class TopicCreateView(CreateView):
    template_name = 'thread/create_topic.html'
    form_class = TopicCreateForm
    model = Topic
    success_url = reverse_lazy('base:top')

    def form_valid(self, form):
        ctx = {'form': form}
        if self.request.POST.get('next', '') == 'confirm':
            return render(self.request, 'thread/confirm_topic.html', ctx) 
        if self.request.POST.get('next', '') == 'back':
            return render(self.request, 'thread/create_topic.html', ctx)
        if self.request.POST.get('next', '') == 'create':
            # メール送信処理
            template = get_template('thread/mail/topic_mail.html')
            mail_ctx = {
                'title': form.cleaned_data['title'],
                'user_name': form.cleaned_data['user_name'],
                'message': form.cleaned_data['message'],
            }
            EmailMessage(
                subject = 'トピック作成:' + form.cleaned_data['title'],
                body = template.render(mail_ctx),
                from_email = 'hogehoge@example.com',
                to = ['admin@example.com'],
                cc = ['admin2@example.com'],
                bcc = ['admin3@example.com'],
            ).send()
            return super().form_valid(form) # 保存
        else:
            # 正常動作ではここは通らない。エラーページへの遷移でも良い
            return redirect(reverse_lazy('base:top'))

        # ページ遷移のように見えるがURL自体は変わっていない（セッションに保存する必要がない）
        # confirm_topic.htmlもlocalhost/thread/create_topic/として表示される

# セッションを使ったトピック投稿画面
class TocicCreateViewBySession(FormView):
    template_name = 'thread/create_topic.html'
    form_class = TopicModelForm

    def post(self, request, *args, **kwargs):
        ctx = {}
        if request.POST.get('next', '') == 'back':
            if 'input_data' in self.request.session:
                input_data = self.request.session['input_data']
                form = TopicModelForm(input_data)
                ctx['form'] = form
            return render(request, self.template_name, ctx)
        elif request.POST.get('next', '') == 'create':
            if 'input_data' in request.session:
                form = self.form_class(request.session['input_data'])
                form.save()
                # Topic.objects.create_topic(
                #     title=request.session['input_data']['title'],
                #     user_name=request.session['input_data']['user_name'],
                #     category_id=request.session['input_data']['category'],
                #     message=request.session['input_data']['message']
                # )
                # メール送信処理は省略
                response = redirect(reverse_lazy('base:top'))
                response.set_cookie('categ_id', request.session['input_data']['category'])
                request.session.pop('input_data') # セッションに保管した情報の削除
                return response
        elif request.POST.get('next', '') == 'confirm':
            form = TopicModelForm(request.POST)
            if form.is_valid():
                ctx = {'form': form}
                # セッションにデータを保存
                input_data = {
                    'title': form.cleaned_data['title'],
                    'user_name': form.cleaned_data['user_name'],
                    'message': form.cleaned_data['message'],
                    'category': form.cleaned_data['category'].id,
                }
                request.session['input_data'] = input_data
                ctx['category'] = form.cleaned_data['category']
                return render(request, 'thread/confirm_topic.html', ctx)
            else:
                return render(request, self.template_name, {'form': form})

    def get_context_data(self):
        ctx = super().get_context_data()
        if 'categ_id' in self.request.COOKIES:
            form = ctx['form']
            form['category'].field.initial = self.request.COOKIES['categ_id']
            ctx['form'] = form
        return ctx



# カテゴリー表示用クラスビュー
class CategoryView(ListView):
    template_name = 'thread/category.html'
    context_object_name = 'topic_list'
    paginate_by = 1 # 1ページに表示するオブジェクト数 サンプルのため1にしています。
    page_kwarg = 'p' # GETでページ数を受けるパラメータ名。指定しないと'page'がデフォルト

    def get_queryset(self):
        return Topic.objects.filter(category__url_code = self.kwargs['url_code'])
     
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['category'] = get_object_or_404(Category, url_code=self.kwargs['url_code'])
        return ctx

# カテゴリー表示用関数ビュー
def show_catgegory(request, url_code):
    if request.method == 'GET':
        page_num = request.GET.get('p', 1)
        pagenator = Paginator(
            Topic.objects.filter(category__url_code=url_code),
            1 # 1ページに表示するオブジェクト数
        )
        try:
            page = pagenator.page(page_num)
        except PageNotAnInteger:
            page = pagenator.page(1)
        except EmptyPage:
            page = pagenator.page(pagenator.num_pages)

        ctx = {
            'category': get_object_or_404(Category, url_code=url_code),
            'page_obj': page,
            'topic_list': page.object_list, # pageでもOK
            'is_paginated': page.has_other_pages,
        }
        return render(request, 'thread/category.html', ctx)


# コメント投稿用view
# FormViewの場合、保存はsuper().form_valid(form)のタイミングで行われる
class TopicAndCommentView(FormView):
    template_name = 'thread/detail_topic.html'
    form_class = CommentModelForm
    
    def form_valid(self, form):
        # comment = form.save(commit=False) 
        # comment.topic = Topic.objects.get(id=self.kwargs['pk'])
        # comment.no = Comment.objects.filter(topic=self.kwargs['pk']).count() + 1
        # comment.save()
        # コメント保存のためsave_with_topicメソッドを呼ぶ
        form.save_with_topic(self.kwargs.get('pk'))
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('thread:topic', kwargs={'pk': self.kwargs['pk']})
    
    def get_context_data(self):
        ctx = super().get_context_data()
        ctx['topic'] = Topic.objects.get(id=self.kwargs['pk'])
        ctx['comment_list'] = Comment.objects.filter(
            topic_id=self.kwargs['pk']).annotate(vote_count=Count('vote')).order_by('no')
        return ctx


class TopicViewAndCommentCreateView(FormView):
    template_name = 'thread/detail_topic.html'
    form_class = CommentModelForm
      
    def form_valid(self, form):
        Comment.objects.create_comment(
            user_name=form.cleaned_data['user_name'],
            message=form.cleaned_data['message'],
            topic_id=self.kwargs['pk'],
            image=form.cleaned_data['image']
        )
        response = super().form_valid(form)
        return response
  
    def get_success_url(self):
         return reverse_lazy('thread:topic', kwargs={'pk': self.kwargs['pk']})
      
    def get_context_data(self):
        ctx = super().get_context_data()
        ctx['topic'] = Topic.objects.get(id=self.kwargs['pk'])
        ctx['comment_list'] = Comment.objects.filter(
            topic_id=self.kwargs['pk']).annotate(vote_count=Count('vote')).order_by('no')
        return ctx

