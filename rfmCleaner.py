import pandas as pd 
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
import numpy as np

class RfmCleaner:
    #Constructor
    def __init__(self, filepath,cc,od,a,format):
        self.df = pd.DataFrame(pd.read_csv(filepath))
        self.customerCode= cc
        self.amount=a
        self.orderDate=od
        self.format=format
        pass
    
    #Takes the date of most recent order by the user and counts the self.amount of days passed and return it as a dataFrame(self.customerCode and Recency). today=0 , yesterday=1, 1 year ago=365
    def addRecency(self):
        self.df[self.orderDate] = pd.to_datetime(self.df[self.orderDate], format=self.format)
        df_recency = self.df.groupby(by=self.customerCode, 
                                as_index=False)[self.orderDate].max()
        df_recency.columns = [self.customerCode, 'LastPurchaseDate']
        recent_date = df_recency['LastPurchaseDate'].max()
        df_recency['Recency'] = df_recency['LastPurchaseDate'].apply(
            lambda x: (recent_date - x).days)
        return df_recency
    
    #Counts the total number of orders made by customer and return it as a dataFrame(self.customerCode and Frequency).
    def addFrequency(self):
        frequency_df = self.df.drop_duplicates().groupby(
            by=[self.customerCode], as_index=False)[self.orderDate].count()
        frequency_df.columns = [self.customerCode, 'Frequency']
        return frequency_df
        
    #Calculate the sum of all the purchased made by user and return it as a dataFrame(self.customerCode and Monetary)
    def addMonetary(self):
        monetary_df = self.df.groupby(by=self.customerCode, as_index=False)[self.amount].sum()
        monetary_df.columns = [self.customerCode, 'Monetary']
        return monetary_df
        
    #Calls addRecency, addFrequency, addMonetary methods merge them by self.customerCode and assigns the objects df method to it.
    def merge(self):
        rfm_df = self.addRecency().merge(self.addFrequency(), on=self.customerCode).merge(self.addMonetary(), on=self.customerCode).drop(
            columns='LastPurchaseDate')
        self.df = rfm_df
    
    #Calls isolate function to adjust outliers, ranks them based on their values and normalizes them in a range of (0,5) 
    def cleanup(self):
        self.merge()
        rank_columns = ['Recency', 'Frequency', 'Monetary']
        for col in rank_columns:
            self.isolate(col)
            if col =='Recency':
                self.df[col + '_rank'] = self.df['iso_'+col].rank(ascending=False)
            else:
                self.df[col + '_rank'] = self.df['iso_'+col].rank(ascending=True)
            self.df[col + '_rank_norm'] = ((self.df[col + '_rank'] - self.df[col + '_rank'].mean()) / self.df[col + '_rank'].std())
            
            self.df[col + '_rank_norm'] = np.interp(self.df[col + '_rank_norm'], (self.df[col + '_rank_norm'].min(), self.df[col + '_rank_norm'].max()), (0, 5))
            self.df.drop(columns=['iso_'+col,col+'_rank'], inplace=True)  # Specify columns to drop and axis=1 to indicate columns


    #finds outliers if it is too small makes it equal to inliers min value and if it is too big makes it equal to inliers max value.
    def isolate(self, col):
        try:
            # Fit the Isolation Forest model
            iso_forest = IsolationForest(n_estimators=100, contamination=0.05, random_state=42)
            iso_forest.fit(self.df[[col]])
            
            # Predict outliers
            outlier_preds = iso_forest.predict(self.df[[col]])

            # Filter out inliers and assign them to a new column
            inliers = self.df[outlier_preds == 1][col]

            # Replace outliers with min/max of inliers
            outliers_mask = outlier_preds == -1
            self.df['iso_'+col] = self.df[col]
            self.df.loc[outliers_mask, 'iso_'+col] = np.where(self.df.loc[outliers_mask, col] < inliers.min(),
                                                            inliers.min(), inliers.max())
        except Exception as e:
            print(f"An error occurred in the isolate method for column '{col}': {e}")

    def clean(self):
        self.cleanup()
        return self.df
        