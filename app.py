from flask import Flask, render_template, jsonify, request
from flask_cors import CORS, cross_origin
from urllib.request import urlopen
import requests
import logging
from bs4 import BeautifulSoup
import pymongo
logging.basicConfig(filename="scrapper.log", level=logging.INFO)

app = Flask(__name__)
@app.route("/")
def index():
    return render_template("index.html")

@app.route('/review', methods = ['POST'])
def result():
    if request.method == "POST":
        try:
            flipkart_link = "https://www.flipkart.com/search?q="
            itemname = request.form['item'].replace(" ","")
            productpage_link = flipkart_link + itemname
            # print(productpage_link)
            productpageopen = urlopen(productpage_link)
            productpage = productpageopen.read()
            productpageopen.close()
            # print(productpage)
            bsproductpage = BeautifulSoup(productpage, 'html.parser')
            # print(bsproductpage)
            parentboxes = bsproductpage.find_all('div', {"class":"_1AtVbE col-12-12"})
            # print(len(parentboxes))
            del parentboxes[0:3]
            childbox = parentboxes[0]
            producturl = "https://www.flipkart.com" + childbox.div.div.div.a['href']
            # print(producturl)
            childproductpage = requests.get(producturl)
            # print(childproductpage)   //This is giving <Response [200]>
            childproductpage.encoding = 'utf-8'
            childproductpage_html = BeautifulSoup(childproductpage.text, 'html.parser')
            # print(childproductpage_html)
            commentboxes = childproductpage_html.find_all('div',{"class":"_16PBlm"})
            # print(len(commentboxes))

            reviews = []
            for commentbox in commentboxes:
                try:
                    name = commentbox.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text
                    # print(name)
                except:
                    logging.info("name")

                try:
                    rating = commentbox.div.div.div.div.text
                    # print(rating)
                except:
                    rating = "no rating"
                    logging.info("rating")

                try:
                    commenthead = commentbox.div.div.div.p.text
                    # print(commenthead)
                except:
                    logging.info("heading")
                
                try:
                    mycomments = commentbox.div.div.find_all('div', {'class':''})
                    # print(mycomments)
                    custComment = mycomments[0].div.text
                    # print(custComment)
                except:
                    logging.info("comments")

                reviewdict = {"Product":itemname, "Name":name, "Rating":rating, "CommentHeading":commenthead, "MyComment":custComment}
                reviews.append(reviewdict)

                logging.info("log my final result {}".format(reviews))

                # Sending data to mongodb
                
                # myclient = pymongo.MongoClient("mongodb+srv://jakiyadeveloper:jakiyadeveloper@mongodbproject.lhvt9bm.mongodb.net/?retryWrites=true&w=majority")
                # mydb = myclient["scrapping"]
                # mycol = mydb["flipkart_scrap"]
                # mycol.insert_many(reviews)

            return render_template("result.html", reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            print(e)
            return "something went wrong"
    else:
        return render_template('index.html')


if __name__ == "__main__":
    app.run()