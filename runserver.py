import os
from flask import Flask, request, redirect, url_for, send_from_directory, jsonify
from flask import render_template
from werkzeug.utils import secure_filename
import itertools

UPLOAD_FOLDER = os.path.dirname(__file__) + "/uploads/"
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


support = 5
confidence = 5
txt = ""
rules = {}
"""Compute candidate 1-itemset"""
C1 = {}
"""total number of transactions contained in the file"""
transactions = 0
D = []

L1 = []


def apriori_gen(Lk_1, k):
    length = k
    Ck = []
    for list1 in Lk_1:
        for list2 in Lk_1:
            count = 0
            c = []
            if list1 != list2:
                while count < length - 1:
                    if list1[count] != list2[count]:
                        break
                    else:
                        count += 1
                else:
                    if list1[length - 1] < list2[length - 1]:
                        for item in list1:
                            c.append(item)
                        c.append(list2[length - 1])
                        if not has_infrequent_subset(c, Lk_1, k):
                            Ck.append(c)
                            c = []
    return Ck


"""function to compute 'm' element subsets of a set S"""


def findsubsets(S, m):
    return set(itertools.combinations(S, m))


"""has_infrequent_subsets function to determine if pruning is required to remove unfruitful candidates (c) using the Apriori property, with prior knowledge of frequent (k-1)-itemset (Lk_1)"""


def has_infrequent_subset(c, Lk_1, k):
    list = []
    list = findsubsets(c, k)
    for item in list:
        s = []
        for l in item:
            s.append(l)
        s.sort()
        if s not in Lk_1:
            return True
    return False


"""frequent_itemsets function to compute all frequent itemsets"""


def frequent_itemsets():
    k = 2
    Lk_1 = []
    Lk = []
    L = []
    count = 0
    transactions = 0
    for item in L1:
        Lk_1.append(item)
    while Lk_1 != []:
        Ck = []
        Lk = []
        Ck = apriori_gen(Lk_1, k - 1)
        # print "-------------------------CANDIDATE %d-ITEMSET---------------------" % k
        # print "Ck: %s" % Ck
        # print "------------------------------------------------------------------"
        for c in Ck:
            count = 0
            transactions = 0
            s = set(c)
            for T in D:
                transactions += 1
                t = set(T)
                if s.issubset(t) == True:
                    count += 1
            if (100 * count / transactions) >= support:
                c.sort()
                Lk.append(c)
        Lk_1 = []
        print "-----------------------FREQUENT %d-ITEMSET------------------------" % k
        print Lk
        print "------------------------------------------------------------------"
        for l in Lk:
            Lk_1.append(l)
        k += 1
        if Lk != []:
            L.append(Lk)

    return L


"""generate_association_rules function to mine and print all the association rules with given support and confidence value"""


def generate_association_rules():
    global txt, rules
    s = []
    r = []
    length = 0
    count = 1
    inc1 = 0
    inc2 = 0
    num = 1
    m = []
    L = frequent_itemsets()
    print "---------------------ASSOCIATION RULES------------------"
    print "RULES \t SUPPORT \t CONFIDENCE"
    print "--------------------------------------------------------"
    for list in L:
        for l in list:
            length = len(l)
            count = 1
            while count < length:
                s = []
                r = findsubsets(l, count)
                count += 1
                for item in r:
                    inc1 = 0
                    inc2 = 0
                    s = []
                    m = []
                    for i in item:
                        s.append(i)
                    for T in D:
                        if set(s).issubset(set(T)) == True:
                            inc1 += 1
                        if set(l).issubset(set(T)) == True:
                            inc2 += 1
                    if 100 * inc2 / inc1 >= confidence:
                        for index in l:
                            if index not in s:
                                m.append(index)
                        # print "Rule#  %d : %s ==> %s %d %d" %(num, s, m, 100*inc2/len(D), 100*inc2/inc1)
                        txt += str("Rule# " + str(num) + ": " + str(s) + " ==> " + str(m) + " " + str(
                            100 * inc2 / len(D)) + " " + str(100 * inc2 / inc1)) + "\n"
                        rules[str(s)] = ([str(num), str(s), str(m), str(
                            100 * inc2 / len(D)), str(100 * inc2 / inc1)])
                        num += 1
    print(txt)

    return rules


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    global transactions, D, L1, support, confidence
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            print('error2')

            return redirect(request.url)

        for fisier in request.files.getlist('file'):
            print("*******")
            # if user does not select file, browser also
            # submit a empty part without filename

            if fisier.filename == '':
                print('error2')

                return redirect(request.url)

            if fisier and allowed_file(fisier.filename):
                filename = secure_filename(fisier.filename)
                # file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

                for line in fisier.stream.readlines():
                    T = []
                    transactions += 1
                    for word in line.split():
                        T.append(word)
                        if word not in C1.keys():
                            C1[word] = 1
                        else:
                            count = C1[word]
                            C1[word] = count + 1
                    D.append(T)
                for key in C1:
                    if (100 * C1[key] / transactions) >= support:
                        list = []
                        list.append(key)
                        L1.append(list)
                print(D)
                res = str(generate_association_rules())
                transactions = 0
                D = []
                L1 = []
                print("intra aici")
                headers= {'Content-Type': 'text/html'}
                return 'sadfgd'

    return ''' <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <p><input type=file name=file>
            <input type=file name=file>
         <input type=submit value=Upload>
    </form>
    '''


@app.route('/asd')
def uploaded_file():
    return render_template("asd.html")


if __name__ == "__main__":
    app.run(threaded=True)
