# encoding = UTF-8
import os
import sqlite3
import urlparse
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import sys
from scrapy.utils.project import get_project_settings

default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)
star_array = []


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def read_star():
    db = sqlite3.connect(get_project_settings()['DATABASE_POSITION'])
    db.row_factory = dict_factory
    cursor = db.cursor()
    cursor.execute('select * from pixiv_item where star is not null ORDER BY -star')
    global star_array, unstar
    star_array = cursor.fetchall()

read_star()


# class MyRequestHandler(BaseHTTPRequestHandler):
#
#     def do_GET(self):
#         """
#         """
#         if self.path == '/':
#             html = u"""
#             <!DOCTYPE html>
#                 <html lang="en">
#                 <head>
#                     <meta charset="UTF-8">
#                     <title>Title</title>
#                     <style type="text/css">
#                         .pixiv-item{
#                             margin: 20px;
#                             width: 200px;
#                             float: left;
#                             display: block;
#                         }
#
#                         .pixiv-item p{
#                             text-align: center;
#                             font-family: "Microsoft YaHei", Monaco, "Courier New", Courier, monospace;
#                         }
#
#
#                         .pixiv-item img{
#                             width: 100%;
#                         }
#                         .outer{
#                             position: relative;
#                             max-width: 1600px;
#                         }margin: 20px;
#                             width: 200px;
#                             float: left;
#                             display: block;
#                         }
#
#                         .pixiv-item p{
#                             text-align: center;
#                             font-family: "Microsoft YaHei", Monaco, "Courier New", Courier, monospace;
#                         }
#
#
#                         .pixiv-item img{
#                             width: 100%;
#                         }
#                         .outer{
#                             position: relative;
#                             max-width: 1600px;
#                         }
#                     </style>
#                 </head>
#                 <body>
#                 <div class="outer">
#             """
#             for item in star_array:
#                 html += u"""
#                     <div class="pixiv-item">
#                         <img src="thumbs/full/{0}.jpg">
#                         <a href="{1}"><p>{2}</p></a>
#                         <p>{3}</p>
#                         <p>{4} like</p>
#                     </div>
#                 """.format(item['id'], item['link'], item['title'].encode('utf-8'), item['publish'], item['star'])
#             html += """</div>
#                     </body>
#                     </html>
#                     """
#             self.send_response(200)
#             self.end_headers()
#             self.wfile.write(html)
#         else:
#             if self.path.endswith('.jpg'):
#                 mimeType = 'image'
#                 print self.path
#                 fp = open(cur + self.path)
#                 self.send_response(200)
#                 print os.path.exists(cur + self.path)
#                 self.send_header('content-type', mimeType)
#                 self.end_headers()
#                 self.wfile.write(fp.readall())
#                 fp.close()

# serveaddr = ('', 8000)
# httpd = HTTPServer(serveaddr, MyRequestHandler)
# print "Base serve is start add is %s port is %d"%(serveaddr[0], serveaddr[1])
# httpd.serve_forever()

html = u"""
    <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Title</title>
            <style type="text/css">
                .pixiv-item{
                    margin: 20px;
                    width: 200px;
                    float: left;
                    display: block;
                }

                .pixiv-item p{
                    text-align: center;
                    font-family: "Microsoft YaHei", Monaco, "Courier New", Courier, monospace;
                }


                .pixiv-item img{
                    width: 100%;
                }
                .outer{
                    position: relative;
                    max-width: 1600px;
                }margin: 20px;
                    width: 200px;
                    float: left;
                    display: block;
                }

                .pixiv-item p{
                    text-align: center;
                    font-family: "Microsoft YaHei", Monaco, "Courier New", Courier, monospace;
                }


                .pixiv-item img{
                    width: 100%;
                }
                .outer{
                    position: relative;
                    max-width: 1600px;
                }
            </style>
        </head>
        <body>
        <div class="outer">
    """
for item in star_array:
    html += u"""
        <div class="pixiv-item">
            <img src="thumbs/{0}.jpg">
            <a href="{1}"><p>{2}</p></a>
            <p>{3}</p>
            <p>{4} like</p>
        </div>
    """.format(item['id'], item['link'], item['title'].encode('utf-8'), item['publish'], item['star'])
html += u"""</div>
        </body>
        </html>
        """
f = open(get_project_settings()['IMAGES_STORE'] + '/view.html', 'w')
f.write(html)
f.flush()
f.close()
