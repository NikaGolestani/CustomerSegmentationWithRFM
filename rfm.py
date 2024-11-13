import pandas as pd 
import matplotlib.pyplot as plt
from sklearn.ensemble import IsolationForest
import numpy as np
from rfmCleaner import RfmCleaner

class Rfm:
    #Constructor
    def __init__(self, filepath,cc,od,a,format):
        self.df = RfmCleaner(filepath,cc,od,a,format).clean()
        pass
    #Sets the data based on clean data.
    def setScore(self,r=0.15,f=0.28,m=0.57):
        s=r+f+m
        r=r/s
        f=f/s
        m=m/s
        self.df['RFM_Score'] = r * self.df['Recency_rank_norm'] + f * self.df['Frequency_rank_norm'] + m * self.df['Monetary_rank_norm']
        
    def setCategory(self, a=4.5, b=4, c=3, d=1.5, r=30):
        if 'RFM_Score' in self.df:
            self.df["Customer_segment"] = np.where(
                self.df['RFM_Score'] > a, "Top Customers",
                np.where(
                    self.df['RFM_Score'] > b, "High Value Customers",
                    np.where(
                        self.df['RFM_Score'] > c, "Medium Value Customers",
                        np.where(
                            self.df['RFM_Score'] > d, 'Low Value Customers',
                            np.where(
                                self.df['Recency'] >= r, 'Lost Customers',
                                np.where(
                                    self.df['Recency'] < r, "New Customers",
                                    "Unknown"
                                )
                            )
                        )
                    )
                )
            )
        else:
            self.df.setScore()
            

    def plotPie(self):
        if 'Customer_segment' not in self.df:
            print("no values to plot")
            return
        plt.pie(self.df.Customer_segment.value_counts(),
		    labels=self.df.Customer_segment.value_counts().index,
		    autopct='%.0f%%')
        plt.show()
        
    def save(self,path):
        self.df.to_csv(path, index=False)