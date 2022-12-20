from django.shortcuts import render, redirect
from .forms import VideoForm
# Create your views here

def upload_video(request):
    if request.method == 'POST':
        form = VideoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('videos')
    else:
        form = VideoForm()
    return render(request, 'upload_video.html', {'form': form})