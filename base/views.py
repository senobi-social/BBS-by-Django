from django.shortcuts import render
from django.views.generic import TemplateView, ListView

from thread.models import Topic

# タイムゾーンの設定
from django.utils import timezone

# 関数ベースビュー
# def top(request):
#   context = {'title': 'Django学習ちゃんねる(仮)'}
#   return render(request, 'base/top.html', context)

class TopView(TemplateView):
    template_name = 'base/top.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['title'] = 'IT学習ちゃんねる(仮)'
        return ctx

class TopicListView(ListView):
    template_name = 'base/top.html'
    # model = Topic
    queryset = Topic.objects.order_by('-created')
    context_object_name = 'topic_list'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.new_list = []

    def get_queryset(self):
        topic_list = Topic.objects.order_by('-created')
        self.new_list = self._make_new_list(topic_list)
        return topic_list

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['new_list'] = self.new_list
        return ctx

    def _make_new_list(self, topic_list):
        def pickup_topic(topic):
            now = timezone.now()
            diff = (now - topic.created).total_seconds() / (60 * 60)
            if diff > 1:
                return False
            else:
                return True
        return list(map(lambda x : x.id ,filter(pickup_topic, topic_list)))