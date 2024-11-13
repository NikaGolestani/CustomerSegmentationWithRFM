from rfm import Rfm

rfm=Rfm("data.csv","CustomerCode","OrderDate","NetAmount",'%d/%m/%Y %H:%M:%S')
rfm.setScore(1,1,1)
rfm.setCategory(4,3,2,1,0)
rfm.plotPie()
rfm.save("rfmresults.csv")