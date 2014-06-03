import urllib, urllib2, cookielib
import re, time
import pickle
#-----------------------------------------------------------------------------------------# 
class SkroutzMerchant():
   username = 'YOUR USERNAME'
    password = 'YOUR PASSWORD'
  
     def __init__(self):
      self.categories = Tree(Category("ROOT", ""))
         self.parser = Parser()
         self.saver = Saver()
         self.opener = self.login()
                
     def login(self):
         cj = cookielib.CookieJar()
         opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
         login_data = urllib.urlencode({'user[username]' : SkroutzMerchant.username, 'user[password]' : SkroutzMerchant.password})
         opener.open('https://merchants.skroutz.gr/merchants/users/login', login_data)
         return opener
  
     def get_categ_children(self, categ_id):
         url = 'https://merchants.skroutz.gr/merchants/products/by_category/' + categ_id
         regex = '<a class="category_link" href="/merchants/products/by_category/(.*?)">'
         categ_children_ids = self.parser.parse(self.opener, url, regex)
         return categ_children_ids
  
     def create_categ_tree(self, categ_node):
         categ_child_ids = self.get_categ_children(categ_node.data.id)
         if len(self.get_categ_children(categ_node.data.id)) != 0:
            for categ_id in categ_child_ids:
               tr_node = TreeNode(Category("A", categ_id))
               categ_node.add_child(tr_node)
               time.sleep(0.5)
               self.create_categ_tree(tr_node)
         else:
            # if it has not children categories then it a leaf node. So it has products.
            self.get_categ_products(categ_node.data)
  
     def get_categ_products(self, categ):
  
         i = 1
         categ_product_ids = []
         while True:
            url = 'https://merchants.skroutz.gr/merchants/products/by_category/' + categ.id +'?page='+str(i)
            regex = '<a href="/merchants/products/show/(.*?)">'
            # returns all product ids
            temp_categ_prod_ids = self.parser.parse(self.opener, url, regex)
            if len(temp_categ_prod_ids) == 0:
               break
            categ_product_ids += temp_categ_prod_ids
  i += 1
  
         for categ_prod_id in categ_product_ids:
            url = 'https://merchants.skroutz.gr/merchants/products/show/'+ categ_prod_id + ''
            regex = '<a href="http://skroutz.gr/s/(.*?)/(.*?).html"'
            # returns 2nd product id and coded name of each product
            prod_stats_id_name = self.parser.parse(self.opener, url, regex) #2nd prod id, coded name
  
            regex = '<span>(.*?)\s\xe2\x82\xac</span>'
            # returns the price of our store
            prod_price = self.parser.parse(self.opener, url, regex)
  
            if len(prod_stats_id_name) != 0: 
               #prod_stats.append(("empty", "empty"))
               url = 'http://skroutz.gr/s/'+ prod_stats_id_name[0][0] +'/'+ prod_stats_id_name[0][1] +'.html'
               regex = '<span class="price" itemprop="lowPrice">(.*?)\s'
               # returns the minimum price of all stores on skroutz for this product
               prod_minprice = self.parser.parse(self.opener, url, regex)
  
               if len(prod_minprice) != 0:
                  categ.products.append(Product(prod_stats_id_name[0][1], prod_price[0], prod_minprice[0]))
  
#-----------------------------------------------------------------------------------------# 
class Saver:
     def save(self, obj):
         file_handler = open('categs_tree.pkl', 'w')
         pickle.dump(obj, file_handler)
  
     def load(self):
         file_handler = open('categs_tree.pkl', 'r')
         categs_tree = pickle.load(file_handler)
         return categs_tree
#-----------------------------------------------------------------------------------------# 
class Category:
     def __init__(self, name, id):
         self.name = name
         self.id = id
         self.products = []
  
     def show(self):
         print "["+self.id+"] "
         for prod in self.products:
            prod.name
#-----------------------------------------------------------------------------------------# 
class Product:
     def __init__(self, name, price, minprice):
         self.name = name
         self.price = price
         self.minprice = minprice
  
     def show(self):
         print "Name: "+self.name+"\nPrice: "+self.price+"\nLow Price: "+self.minprice+"\n" 
  
class Parser:
     def parse(self, opener, url, regex):
         resp = opener.open(url).read()
         regComp = re.compile(regex)
         regRes = re.findall(regComp, resp)
         return list(set(regRes))
                
#-----------------------------------------------------------------------------------------# 
class TreeNode(object):
     def __init__(self, data):
         self.data = data
         self.children = []

     def add_child(self, obj):
         self.children.append(obj)
  
     def show(self):
         #print "I am a TreeNode"
         self.data.show()
#-----------------------------------------------------------------------------------------# 
class Tree:
     def __init__(self, root):
         self.root = TreeNode(root)
                
     def preorder_trav(self, node):
         if node is not None:
            node.show() #print node.data
            if len(node.children) != 0:
               #print "("+ node.data + ")"
               for n in node.children:
                  #n.show() #print n.data
                  self.preorder_trav(n)
        
     def get_leaf_nodes(self):
         leafs = []
         def _get_leaf_nodes( node):
            if node is not None:
               if len(node.children) == 0:
                  leafs.append(node)
               for n in node.children:
                  _get_leaf_nodes(n)
         _get_leaf_nodes(self.root)
         return leafs

                        
#-----------------------------------------------------------------------------------------# 
if __name__ == '__main__':
  
     sm = SkroutzMerchant()
     sm.create_categ_tree(sm.categories.root)
     sm.saver.save(sm.categories)
     loaded_tree = sm.saver.load()
     leaf_list = loaded_tree.get_leaf_nodes()
     fh = open('store.txt', 'w+')
     for lf in leaf_list:
         for cp in lf.data.products:
            if cp.minprice < cp.price:
               fh.write("ONOMA: "+cp.name+"\nTIMH katastimatos mas: "+cp.price+"\nXAMHLOTERH TIMH: "+cp.minprice+"\n>>>>YPARXEI FTHINOTEROS!!\n\n")
  
     fh.close()
