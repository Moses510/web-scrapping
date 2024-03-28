from flask import Flask, render_template, request,jsonify
from flask_cors import CORS,cross_origin
import requests
from bs4 import BeautifulSoup as bs
from urllib.request import urlopen as uReq
import logging
import pymongo
logging.basicConfig(filename="scrapper.log" , level=logging.INFO)

app = Flask(__name__)

@app.route("/", methods = ['GET'])
def homepage():
    return render_template("index.html")

@app.route("/review" , methods = ['POST' , 'GET'])
def index():
    if request.method == 'POST':
        try:
            searchString = request.form['content'].replace(" ","")
            flipkart_url = "https://www.flipkart.com/search?q=" + searchString
            uClient = uReq(flipkart_url)
            flipkartPage = uClient.read()
            uClient.close()
            flipkart_html = bs(flipkartPage, "html.parser")
            bigboxes = flipkart_html.findAll("div", {"class": "_1AtVbE col-12-12"})
            del bigboxes[0:3]
            box = bigboxes[0]
            productLink = "https://www.flipkart.com" + box.div.div.div.a['href']
            prodRes = requests.get(productLink)
            prodRes.encoding='utf-8'
            prod_html = bs(prodRes.text, "html.parser")
            print(prod_html)
            commentboxes = prod_html.find_all('div', {'class': "_16PBlm"})

            filename = searchString + ".csv"
            fw = open(filename, "w")
            headers = "Product, Customer Name, Rating, Heading, Comment \n"
            fw.write(headers)
            reviews = []
            for commentbox in commentboxes:
                try:
                    #name.encode(encoding='utf-8')
                    name = commentbox.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text

                except:
                    logging.info("name")

                try:
                    #rating.encode(encoding='utf-8')
                    rating = commentbox.div.div.div.div.text


                except:
                    rating = 'No Rating'
                    logging.info("rating")

                try:
                    #commentHead.encode(encoding='utf-8')
                    commentHead = commentbox.div.div.div.p.text

                except:
                    commentHead = 'No Comment Heading'
                    logging.info(commentHead)
                try:
                    comtag = commentbox.div.div.find_all('div', {'class': ''})
                    #custComment.encode(encoding='utf-8')
                    custComment = comtag[0].div.text
                except Exception as e:
                    logging.info(e)

                mydict = {"Product": searchString, "Name": name, "Rating": rating, "CommentHead": commentHead,
                          "Comment": custComment}
                reviews.append(mydict)
            logging.info("log my final result {}".format(reviews))

            
            client = pymongo.MongoClient("mongodb+srv://pwskills:pwskills@cluster0.ln0bt5m.mongodb.net/?retryWrites=true&w=majority")
            db =client['scrapper_eng_pwskills']
            coll_pw_eng = db['scraper_pwskills_eng']
            coll_pw_eng.insert_many(reviews)

            return render_template('result.html', reviews=reviews[0:(len(reviews)-1)])
        except Exception as e:
            logging.info(e)
            return 'something is wrong'
    # return render_template('results.html')

    else:
        return render_template('index.html')


if __name__=="__main__":
    app.run(host="0.0.0.0")






# from flask import Flask, render_template, request, jsonify
# from flask_cors import CORS, cross_origin
# import requests
# from bs4 import BeautifulSoup as bs
# from urllib.request import urlopen
# import pymongo

# application = Flask(__name__)   #initializing the Flask app
# app = application

# @app.route('/', methods=['GET'])  #route to display the home page
# @cross_origin()
# def homePage():
#     return render_template('index.html')

# @app.route('/review', methods=['POST', 'GET'])  #route to show the review comments in a web UI
# @cross_origin()
# def index():
#     if request.method == 'POST':
#         try:
#             searchString = request.form['content'].replace(' ', '')
#             flipkart_url = 'https://www.flipkart.com/search?q=' + searchString
#             uClient = urlopen(flipkart_url)   # it will open the url
#             flipkartPage = uClient.read()     # it will read the page
#             uClient.close()                   # it will close the page
#             flipkart_html = bs(flipkartPage, 'html.parser')      # it will beautify the html page
#             bigbox = flipkart_html.find_all('div', {'class': '_1AtVbE col-12-12'})  # it will gather the boxes details
#             del bigbox[0:2] 
#             del bigbox[24:]
#             reviews = []  #empty list

#             for i in bigbox:
#                 productLink = 'https://www.flipkart.com' + i.div.div.div.a['href']
#                 prodRes = requests.get(productLink) # landing into particular product page
#                 prodRes.encoding = 'utf-8'
#                 prod_html = bs(prodRes.text, "html.parser")
#                 print(prod_html)
#                 commentboxes = prod_html.find_all('div', {'class': "_16PBlm"})

#                 for commentbox in commentboxes:
#                     try:
#                         name = commentbox.div.div.find_all('p', {'class': '_2sc7ZR _2V5EHH'})[0].text
#                     except:
#                         name = 'No Name'

#                     try:
#                         rating = commentbox.div.div.div.div.text
#                     except:
#                         rating = 'No Rating'

#                     try:
#                         commentHead = commentbox.div.div.div.p.text
#                     except:
#                         commentHead = 'No commentHead'

#                     try:
#                         custComment = commentbox.div.div.find_all('div', {'class': ''})[0].text
#                     except Exception as e:
#                         print('Exception while creating the dictionary', e)

#                     mydict = {'product': searchString, 'Name': name, 'Rating': rating, 'CommentHead': commentHead,
#                               'Comment': custComment}
#                     reviews.append(mydict)

#             # # Updating the record to MongoDB
#             # client = pymongo.MongoClient(
#             #     "mongodb+srv://pwskills:pwskills@cluster0.ln0bt5m.mongodb.net/?retryWrites=true&w=majority")
#             # db = client['review_scrap']
#             # review_col = db['review_scrap_data']
#             # review_col.insert_many(reviews)

#             # Writing to CSV
#             filename = searchString + ".csv"
#             with open(filename, "w") as fw:
#                 # headers = "Product, Customer Name, Rating, Heading, Comment \n"
#                 # fw.write(headers)
#                 for review in reviews:
#                     fw.write(
#                         f"{review['product']}, {review['Name']}, {review['Rating']}, {review['CommentHead']}, {review['Comment']} \n")

#             return render_template('result.html', reviews=reviews[0:(len(reviews)-1)])

#         except Exception as e:
#             print('The Exception message is', e)
#             return 'Something Went Wrong'
#     else:
#         return render_template('index.html')

# if __name__ == "__main__":
#     app.run(host="0.0.0.0")
  
                    

    



