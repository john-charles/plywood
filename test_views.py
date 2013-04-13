import shutil
from plywood.views import View
from plywood.http import PageResponse

PAGE = '''
<html>
    <body>
        <h1>Plywood Test Web Application</h1>
        %(body)s
    </body>
</html>
'''

class Home(View):
    
    def __call__(self):
        
        if 'you_views' in self.request.session:
            you_views = self.request.session['you_views']
        else:
            you_views = 0
            
        special = self.request.query.get('special','Not Entered')
            
        self.request.session['you_views'] = you_views + 1
        
        page = '''You've viewed this page %s times!<br>
        <a href="/upload/">Upload a file!</a><br>
        Special value is &quot;%s&quot;''' % (you_views, special)
        return PageResponse(self.request, PAGE % {'body':page})
    
class Upload(View):
    
    def __call__(self):
        
        if self.request.is_post:
            my_file = self.request.post['my_file']
            ds_file = open("file.jpg",'wb')
            shutil.copyfileobj(my_file, ds_file)
            ds_file.close()
            
        page = '''
        <form method="post" action="/upload/" enctype="multipart/form-data">
            <input type="hidden" value="%s" name="csrf_token">
            <input type="file" name="my_file">
            <input type="submit" value="Upload">
        </form>
        <a href="/">Back</a>
        ''' % self.request.csrf_token
        
        return PageResponse(self.request, PAGE % {'body':page})
        
        