"""
Created on Tue Apr 22 10:31:37 2026

@author: RoseAlewine
Rose.Alewine95@gmail.com

This tool is an automated decision system that ranks options based on
weighted features reflecting your preferences. In other words,
it helps you determine what to choose based on what matters most to you."""
#####################################################################

import streamlit as st
import pandas as pd
import numpy as np

st.title("**Let Me Help You Clear Your Mind!**")
st.markdown("**Easier decision-making with a decision support tool for structured choices**")
st.write("This tool is an automated decision system that ranks options based on"
         "weighted features reflecting your preferences. In other words, "
         "it helps you determine what to choose based on what matters most to you."
         )
st.markdown("""
### How it works
1. Upload your dataset  
2. Define whether each feature is positive or negative  
3. Assign importance using sliders  
4. Click **Run Model**
""")
#####################################################################
#   Upload file
#####################################################################
st.divider()
st.header("📂 Upload Data")
uploaded_file = st.file_uploader("Upload your Excel file", type=["xlsx"])
st.write("The alternatives must be in the first column, with feature scores"
         " in the following columns, labeled with each feature name.")
if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.write("### Data Preview")
    st.dataframe(df)

    Attributes = list(df.columns[1:])
    
#####################################################################
#   Impact Selection (P / N)
#####################################################################
    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Select Feature Impacts")
        # impact selectors here
        st.write("**Positive: higher scores are better; Negative: lower scores are better**")
        Impact = []
        
        for item in Attributes:
            choice = st.selectbox(
                f"{item} impact",
                ["P (Positive)", "N (Negative)"],
                key=item
            )
            Impact.append("P" if choice.startswith("P") else "N")

#####################################################################
#   Weights (Sliders)
#####################################################################
        
    with col2:
        st.subheader("Select Feature Weights")
        # sliders here
        
        
        # st.write("### Select Feature Impacts")
        
    
        # st.write("### Select Feature Weights")
        st.write("**Focus on the relative importance of the features.**")
        weights = []
    
        for item in Attributes:
            w = st.slider(f"Weight for {item}", 0.0, 10.0, 5.0)
            weights.append(w)

#####################################################################
#   Weights Normalization
#####################################################################
        weights = np.array(weights)
        FinalWeights = weights/np.sum(weights)

#####################################################################
#   Calculations: Running
#####################################################################
    # col1, col2, col3 = st.columns([1,2,1])

    # with col2:
    #     st.button("🚀 Run Model", type="primary")    

    if st.button("🚀 Run Model", type="primary"):
        st.divider()
        
        Numbers=df.iloc[:, 1:]
        Numbers=Numbers.to_numpy()

        Square = (Numbers)**2
        SUMCol=[]
        for i in range (len(Attributes)):
            SUMCol.append(sum(Square[:,i]))
            
        SQSum=np.sqrt(SUMCol)

        NonLinear = np.zeros((len(df.index),len(Attributes))) #So Impo for introducing a new matrix

        for i in range(len(df.index)):
            for j in range(len(Attributes)): 
                NonLinear[i,j]=Numbers[i,j]/SQSum[j]  
                
        CrossMatrix=np.zeros((len(df.index),len(Attributes)))
        RankMatrix=np.zeros((len(df.index),len(Attributes)))

        for i in range(len(df.index)):
            for j in range(len(Attributes)): 
                CrossMatrix[i,j]=NonLinear[i,j]*FinalWeights[j]
                
                if(Impact[j]=="P"):
                    RankMatrix[i,j]=CrossMatrix[i,j]
                else: #Impact: Negative (N)
                    RankMatrix[i,j]=-CrossMatrix[i,j]
                    
                    
        Ranking=[]
        for i in range(len(df.index)): 
           per=0
           for j in range(len(Attributes)): 
               per+=(RankMatrix[i,j])
           Ranking.append(per)     
           
#####################################################################
#   More Fun: ELECTRE: Let's eliminate options, MOST USEFUL WITH SO MANY ALTs
#####################################################################
#*********************Matrices***************************************
    
        CIni=[]
        DIni=[]
        
        for i in range(len(df.index)):
            for k in range((len(df.index))):
                if (i!=k):
                    
                    CSublist=[]
                    DSublist=[]
        
                    for j in range(len(Attributes)): 
                        
         
                        if(Impact[j]=="P"):
                            if (CrossMatrix[i,j]-CrossMatrix[k,j])>=0:
                                CSublist.append(Attributes[j])
                            else:
                                DSublist.append(Attributes[j])
                                
                        else: #Negative
                            if (CrossMatrix[i,j]-CrossMatrix[k,j])<=0:
                                CSublist.append(Attributes[j])
                            else:
                                DSublist.append(Attributes[j])
        
        
                    CIni.append([i,k,CSublist])    
                    DIni.append([i,k,DSublist])
                    
        CMatrix=np.zeros((len(df.index),len(df.index)))
        
        for item in CIni:
            CCoef=0
            for s in (item[2]):
                indexx=Attributes.index(s)
                CCoef+=FinalWeights[indexx]
                
            CMatrix[item[0],item[1]]=CCoef   
                    
        
        ############################################################
        ############################################################
        # D MATRIX
        DMatrix=np.zeros((len(df.index),len(df.index)))
        for i in range(len(df.index)):
            for k in range((len(df.index))):
        
                if (i!=k):
        
                    Delta=[]
                    AllDeltas=[]
        
                    for j in range(len(Attributes)): 
        
                        AllDeltas.append(abs((CrossMatrix[i,j]-CrossMatrix[k,j])))
                       
                        for item in DIni:
                    
                            if item[0]==i and item[1]==k:
                                if (Attributes[j] in item[2]):
                                  
                                    Delta.append(abs((CrossMatrix[i,j]-CrossMatrix[k,j])))
                                  
                           
                    MaxAll=max(AllDeltas)
                    
                    if len(Delta) == 0:
                        MaxUp = 0
                    else:
                        MaxUp = max(Delta)
                
                    Dvalue=MaxUp/MaxAll
                    DMatrix[i,k]=Dvalue
                    
        Carrays=0    
        Darrays=0   
        num=0  #Counter         
        for i in range(len(df.index)):
            for k in range((len(df.index))):
                if i!=k:
                    Carrays+=CMatrix[i,k]
                    Darrays+=DMatrix[i,k]
                    num+=1
        
        
        Cbar=Carrays/num
        Dbar=Darrays/num
        
        
        #########################################################
        #########################################################   
        # E & F Matrix
        
        EMatrix=np.zeros((len(df.index),len(df.index)))
        FMatrix=np.zeros((len(df.index),len(df.index)))
        for i in range(len(df.index)):
            for k in range((len(df.index))):
                if (i!=k):
                    
                    if CMatrix[i,k]>=Cbar:
                        EMatrix[i,k]=1
                        
                    if DMatrix[i,k]<=Dbar:
                        FMatrix[i,k]=1
        
        #########################################################
        # G Matrix
        
        GMatrix=np.zeros((len(df.index),len(df.index)))
        for i in range(len(df.index)):
            for k in range(len(df.index)): 
                GMatrix[i,k]=EMatrix[i,k]*FMatrix[i,k]
        
        
        ListRS=[]
        ListCS=[]
        for i in range(len(df.index)):
            RowSum=0
            for k in range(len(df.index)): 
                
                RowSum+=GMatrix[i,k]
            ListRS.append(RowSum)
        
        for k in range(len(df.index)):
            ColSum=0
            for i in range(len(df.index)): 
                
                ColSum+=GMatrix[i,k]
            ListCS.append(ColSum)    
                
        
#####################################################################
#   RESULTS
#####################################################################
    # WinRate = np.sum(GMatrix, axis=1)
    # LostRate = np.sum(GMatrix, axis=0)
    
    # 'Win Rate':ListRS,'Lost Rate':ListCS
        Conclusion = pd.DataFrame({'Alternative': df.iloc[:,0],
                                   'Win Rate':ListRS,'Lost Rate':ListCS})
    
        # Conclusion = pd.DataFrame({
        #     "Alternative": df.iloc[:, 0],
        #     "Win Rate": WinRate,
        #     "Lost Rate": LostRate
        # })
        
        st.header("📈 Results")
    
        st.write("### ELECTRE Results: Win/Lost Rates")
        st.dataframe(Conclusion)
    
        st.write("### Simple Ranking")
        results = pd.DataFrame({
            "Alternative": df.iloc[:, 0],
            "Score": Ranking
        }).sort_values(by="Score", ascending=False)
    
        # st.dataframe(results)
        
        # results.style.highlight_max(subset=["Score"])
        st.dataframe(results.style.highlight_max(subset=["Score"],axis=0))
        
        st.divider()
        
        col1, col2 = st.columns(2)

        with col1:
            st.success(f"🏆 Best choice:{results.iloc[0,0]}")

        with col2:
            st.error(f"📉 Least preferred: {results.iloc[-1,0]}")
        # st.success(f"🏆 Best choice: {results.iloc[0,0]}")
        # st.error(f"📉 Least preferred: {results.iloc[-1,0]}")
               
#####################################################################

        csv1 = results.to_csv(index=False).encode('utf-8')
        # csv2= Conclusion.to_csv(index=False).encode('utf-8')
        
        st.download_button("📥 Download Ranking",csv1,"Ranking.csv","text/csv")#,key="download_results_1")
        # st.download_button("📥 Download Win/Lost Rates",csv2,"WinLostRates_ELECTRE.csv","text/csv")#,key="download_results_1")
       
        # st.subheader("📊 Ranking Visualization")
        # st.bar_chart(results.set_index("Alternative"))
        
        # st.subheader("⚖️ Win vs Loss")
        # st.bar_chart(Conclusion.set_index("Alternative")[["Win Rate", "Lost Rate"]])