
import logging
from pymongo import MongoClient 
class CSV_Operators:
    def __init__(self,path, delimiter=',', comma_converted = False):
        '''
        Parameters are:
        path: the file path for the csv file
        delimiter: is the values delimiter (default = ',')
        '''
        
        #open a log file for storing logs
        logging.basicConfig(filename="task.log", level = logging.INFO, format='%(levelname)s: %(asctime)s %(message)s', 
                            datefmt='%m/%d/%Y %I:%M:%S %p')
        
        #Initialization
        self._path = path
        self._delimiter = delimiter
        self._comma_converted = comma_converted
    
    def CSV_to_Dict(self):
        '''
            This Function is used to convert each record in a CSV file into a dictionary using the file management, then append all dictionaries into one
            list suitable for MongoDB insertion.
            This function returns the list of dictionaries
        '''
        #define a sub-container dictionary
        Dict = {}
        #define the main conainer list
        self.CSV_List = []
        
        logging.info(f'Trying to convert the {self._path} file into a Mongo insertion list!')
        try:
            with open(self._path,'rt', encoding="utf8") as f:
                logging.info(f'{self._path} is opened successfully.\t Start converting....')
                cols = f.readline()[:-1].split(self._delimiter)
                text = f.read().rstrip()

                for line in text.split('\n'):
                    line = line.split(self._delimiter)
                    if self._comma_converted == True:
                        Dict = {cols[i]: line[i].replace(',','.') for i in range(len(cols))}
                    else:
                         Dict = {cols[i]: line[i] for i in range(len(cols))}
                    self.CSV_List.append(Dict)
        except Exception as e:
            logging.error(f'An exception error has occurred! Details: {e}')
            logging.warning('Convertion process is stopped!')
        finally:
            if f.closed==False:
                f.close()
        logging.info(f'File {self._path} is closed and converted successfully.')    
        
        return self.CSV_List

     
    def getCSVData(self):
        return self.CSV_list
    
    def setPath(self, path):
        self._path = path
        logging.info(f'File path is set to {self._path} successfully.') 
        
    def setDelimiter(self, delimiter):
        self._delimiter = delimiter
        logging.info(f'Delimiter is set to {self._delimiter} successfully.') 
    
    def setComma_Converted(self, comma_converted):
        self._comma_converted = comma_converted
        logging.info(f'Comma Coverted Parameter is set to {self._comma_converted} successfully.') 
        
    def isCommaConverted(self):
        return self._comma_converted
    
    def getDelimiter(self):
        return delimiter
        







class database_operation:
    def __init__(self,USR, PW, DB_NAME, C_NAME):
        '''
        This class is used for MongoDB database operations with Atlas platform.
        It takes five parameters: USR is the mongo username, PW is the mongo password, DB_NAME is the name of the created 
        database, C_NAME is the name of the data collection
        '''
        self.__USR = USR
        self.__PASS = PW
        self._DB_NAME = DB_NAME
        self._COLLECTION_NAME = C_NAME
        self._database = ''
        self._collection = ''
        self._client = ''
        
        #Create the connection url
        self.CONNECTION_URL = f"mongodb+srv://{self.__USR}:{self.__PASS}@cluster0.jag1c.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
        #Create the database log file initialization
        logging.basicConfig(filename="task.log", level = logging.INFO, 
                            format='%(levelname)s: %(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
        
        
    #Connect and create database
    def createDataWarehouse(self):
        '''
            This function is used to create a database and its collectoin in mongoDB.
            It returns client object, database object and collection object
        '''

        try:

            # Establish a connection with mongoDB
            client = MongoClient(self.CONNECTION_URL)
            database = client.test

            # Create a DataBase
            database = client[self._DB_NAME]

            # Create a Collection Name
            collection = database[self._COLLECTION_NAME]

            try:
                client.list_database_names()
                logging.info(f' database and collection Successfully created!')
                self._database = database
                self._client = client
                self._collection = collection
                return True
            
            except Exception as e:
                logging.error(f'Authentication error, cannot Connect to MongoDB server, please check the connection url {self.CONNECTION_URL}\n {e}')

        except Exception as e:
            logging.error(f'Error! {e}')
              
        
        return False


    
    #verify whether we have our collection in the list or not 
    def checkExistence_COL(self, DB_NAME = '', COLLECTION_NAME = '' ):
        """
        Used to verify the existence of current collection name in a database
        It takes two variables: Database name (default object database name) and Collection name (default object collection name). 
        """
        if DB_NAME == '':
            DB_NAME = self._DB_NAME 
        if COLLECTION_NAME == '':
            COLLECTION_NAME = self._COLLECTION_NAME
        
        collection_list = self._database.list_collection_names()

        if COLLECTION_NAME in collection_list:
            logging.info(f"Collection:'{COLLECTION_NAME}' in Database:'{DB_NAME}' exists")
            return True

        logging.warning(f"Collection:'{COLLECTION_NAME}' in Database:'{DB_NAME}' does not exists OR \n\
        no documents are present in the collection")
        return False
    
    #Insert a CSV file into a collection
    def insertFromCSV(self, CSVPath, delimiter = ',', convert_comma_to_dot = False):
        '''
        This function is used to insert a whole CSV file into a Mongo database collection.
        It takes the collection name and the CSV file path, convert_comma_to_dot is set to True if there is a misplaced comma 
        instead of dot in floating point numbers (make sure the file is semi-colon separator) 
        '''
        self.comma_converted = convert_comma_to_dot
        
        try:
            ops = CSV_Operators(CSVPath, delimiter, convert_comma_to_dot)
            self._collection.insert_many( ops.CSV_to_Dict())
            logging.info(f'The complete CSV file ({CSVPath}) is insterted successfully!')
            return True
        except Exception as e:
             logging.error(f'ERROR: {e}')
        return False


    def insertList(self, DataList):
        '''
        This function is used to insert a list of documents into a Mongo database collection.
        It takes the collection name (default object collection name) and list of documents
        '''
        try:
            self._collection.insert_many(DataList)
            logging.info(f'The whole data is insterted successfully into collection!')
            return True
        except Exception as e:
             logging.error(f'ERROR: {e}')
        return False

        
    def insertDocument(self, Dict):
        '''
        This function is used to insert one document into a Mongo database collection.
        It takes the collection name (default object collection) and the document dictionary 
        '''

        try:
            self._collection.insert_one(Dict)
            logging.info(f'One document is insterted successfully into collection!')
            return True
        except Exception as e:
             logging.error(f'ERROR: {e}') 
        return False


    def fetchDocuments(self, condition={}):
        '''
        This function is used to fetch all data from a collection based on specific condition.
        It takes collection name (default object collection) and coonditon and return data. 
        Condition should be written inside {}
        '''
 
        try:
            output=[]
            for doc in self._collection.find(condition) :
                output.append(doc)
            return output  
        except Exception as e:
             logging.error(f'ERROR: {e}')
                
                

    def deleteDocuments(self, condition={}):
        '''
        This function is used to delete one or more documents from the collection based on specific condition.
        It takes the collection name and the document dictionary.
        Takecare: Default condition delete all data.
        '''
        if self.checkExistence_COL():
            try:
                self._collection.delete_many(condition)
                logging.info(f'Records are deleted successfully from collectino!')
                return True
            except Exception as e:
                 logging.error(f'ERROR: {e}') 
            return False
        else:
            logging.error(f'No data exist in  collection!')
            return False
 

    def dropCollection(self):
        '''
        This function is used to drop the whole collection from the database 
        '''
        if self.checkExistence_COL():
            try:
                self._collection.drop()
                logging.info(f'Ooops! The Collection is droped competely!')
                return True
            except Exception as e:
                 logging.error(f'ERROR: {e}')
            return False
        else:
            logging.error(f'No data exist in  collection!')
            return False

       
    
    def updateCollection(self, filter_pair={}, set_pair={}):
        '''
        This function is used to update one or more documents from a collection 
        '''
        if self.checkExistence_COL():
            try:
                self._collection.update_many(filter_pair,set_pair)
                logging.info(f'Documents are updated successfully in the  collection!')
                return True
            except Exception as e:
                 logging.error(f'ERROR: {e}')
            return False
        else:
            logging.error(f'No data exist in  collection!')
            return False