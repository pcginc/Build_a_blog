#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import os
import webapp2
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
                              autoescape = True)

class Handler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class Blog(db.Model):
    title = db.StringProperty(required = True)
    blog = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

class NewPost(Handler):
    #render page to display title and newpost form
    def render_front(self, title="", blog="", error=""):
        self.render("post.html", title=title, blog=blog, error=error,)

    def get(self):
        self.render_front()

    def post(self):
        title = self.request.get("title")
        blog = self.request.get("blog")

        if title and blog:
            b = Blog(title = title, blog = blog)
            b.put()

            self.redirect("/")
        else:
            error = "We need both a title and a blog post!"
            self.render_front(title, blog, error = error)

#class BlogList(Handler):
    #create page to display to blgos saved by title and blog
    #redirect to main blog page
class BlogList(Handler):
    def get(self):
        blogs = db.GqlQuery("SELECT * FROM Blog ORDER BY created DESC LIMIT 5")
        self.render("bloglist.html", blogs = blogs)


class MainPage(Handler):
    def render_front(self, title="", blog="", error=""):
        blogs = db.GqlQuery("SELECT * FROM Blog "
                           "ORDER BY created DESC ")

        self.render("front.html", title=title, blog=blog, error=error, blogs=blogs)

    def get(self):
        self.render_front()

    def post(self):
        title = self.request.get("title")
        blog = self.request.get("blog")

        if title and blog:
            b = Blog(title = title, blog = blog)
            b.put()

            self.redirect("/")
        else:
            error = "we need both a title and some artwork!"
            self.render_front(title, blog, error = error)

class ViewPostHandler(Handler):
    def get(self, post_id):
        blog = Blog.get_by_id(int(post_id))

        if blog:
            self.render("bloglist.html", blog = blog)
        else:
            error = "No blog by that id"
            self.response.write(error)

app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/newpost', NewPost),
    ('/blog', BlogList),
    webapp2.Route('/blog/<post_id:\d+>', ViewPostHandler)

], debug=True)
