////////a////////////////
//Writed by nyan
//used for DT5742
//Just for distribution of waveform
//@2023.10.
//Modified: Added separate timing variables for velocity measurement
//////////////
#include "rootheader.h"

using namespace std;

void Get_AllValue_Measure_new()
{
    ifstream readFile("0000.txt", ios::in);

    TTree *t1 = new TTree("t1", "");
    //
    const int numPoint = 1024;
    const int numChannel = 2;
    //
    int event_num=0;
    int Index=1024;
    int TrigtagTime[Index];
    float rms = 0.0;
    float base = 0.0;
    float overshoot = 0.0;
    float overshoot_Last = 0.0;
    float amp = 0.0;
    int Index_minamp = 0;
    int Index_minamp1 = 0;  // NEW: Peak position for channel 0 (upper detector)
    int Index_minamp2 = 0;  // NEW: Peak position for channel 1 (lower detector)
    float area = 0.0;
	float area2 = 0.0;
    int ADC[Index];
    int ADC2[Index];
    int Index_ADC[Index];
    //


    //double Charge;
    //
    t1->Branch("event_num", &event_num,"evtNum/I");
    t1->Branch("Index", &Index,"Index/I");
    t1->Branch("TrigtagTime", &TrigtagTime,"TrigtagTime[Index]/I");
    t1->Branch("base",&base,"base/F");
    t1->Branch("rms",&rms,"rms/F");
    t1->Branch("overshoot",&overshoot,"overshoot/F");
    t1->Branch("overshoot_Last",&overshoot_Last,"overshoot_Last/F");
    t1->Branch("amp",&amp,"amp/F");
    t1->Branch("Index_minamp",&Index_minamp,"Index_minamp/I");
    t1->Branch("Index_minamp1",&Index_minamp1,"Index_minamp1/I");  // NEW
    t1->Branch("Index_minamp2",&Index_minamp2,"Index_minamp2/I");  // NEW
    t1->Branch("area",&area,"area/F");
	t1->Branch("area2",&area2,"area2/F");
    t1->Branch("ADC",&ADC,"ADC[Index]/I");
    //t1->Branch("ADC2",&ADC2,"ADC2[Index]/I");
    t1->Branch("Index_ADC",&Index_ADC,"Index_ADC[Index]/I");
    //t1->Branch("Charge",&Charge,"Charge/D");

    //
    string line;
    int lineCount = 0;
    for(int i = 0; getline(readFile, line); i++){
        lineCount++;
        event_num = floor(lineCount / numChannel);

        if (lineCount % numChannel == 0) {
            istringstream iss(line);
           //peak
           int index_min = 0;
         int peak_min = 99999;
           double value;
           int nsp =0;
           while (iss >> value) {
        ADC[nsp] = value;
           Index_ADC[nsp] = nsp;
           //cout<<"T1:  "<<ADC[nsp]<<endl;
           //cout<<"T1index:  "<<Index_ADC[nsp]<<endl;
           nsp++;
           }

           for(int n=0; n< 1024; n++){
              if(peak_min>ADC[n] && n>420 && n<550){
               peak_min = ADC[n];
               //cout<<"T1 min:  "<<peak_min<<endl;
           index_min = Index_ADC[n];
              }
           }

           //baseline
           int GetbaseLine =1;
       if(GetbaseLine == 1){
              vector<int> rmsbase;

           int sum_baseLow = 0;
          int num_baseLow = 0;
           vector<int> rmsbaseLow;
              for(int kLow = 0; kLow < 100; kLow++){
            sum_baseLow += ADC[kLow];
              num_baseLow++;
             rmsbaseLow.push_back(ADC[kLow]);
              }
              double baseLow = sum_baseLow / num_baseLow;

              int sum_baseUp = 0;
            int num_baseUp = 0;
              vector<int> rmsbaseUp;
              for(int kUp = 900; kUp < 1000; kUp++){
                sum_baseUp += ADC[kUp];
           num_baseUp++;
                rmsbaseUp.push_back(ADC[kUp]);
              }
            double baseUp = sum_baseUp / num_baseUp;

              if(baseLow>baseUp){
           base = baseUp;
               rmsbase = rmsbaseUp;
              }
              else{
                 base = baseLow;
                 rmsbase = rmsbaseLow;
              }
              rmsbaseUp.clear();
              rmsbaseLow.clear();
///UP base//
              //rms
              rms = TMath::RMS(rmsbase.size(),&rmsbase[0]);
           rmsbase.clear();
        }
       //amp/overbase
        double sum_amp = 0;
         int count= 0;
           vector<int> overbase;
           for(int j = index_min - 50; j<index_min + 50; j++){
               sum_amp +=ADC[j];
               //cout<<"T2:   "<<sum_amp<<endl;
          count++;
               overbase.push_back(ADC[j]);
           }
           overshoot = (TMath::MaxElement(overbase.size(),&overbase[0]) - base) * (1/pow(2,12)) * 1000;
           overbase.clear();

           amp = (base - peak_min)* (1/pow(2,12))*1000;//U:mv
           //area1
           Index_minamp = index_min;
           Index_minamp1 = index_min;  // NEW: Save channel 0 peak position
           area = (count*base - sum_amp)*(1/pow(2,12))*1000/50 * 1;//Charge: pC

          //overshoot_Last
        double sum_amp_Last =0;
          vector<int> overbase_Last;
          for(int b = 800;b<1024;b++){
              //sum_amp_Last +=ADC[b];
                overbase_Last.push_back(ADC[b]);
      }
        overshoot_Last = (TMath::MaxElement(overbase_Last.size(),&overbase_Last[0]) - base) * (1/pow(2,12))*1000;
          overbase_Last.clear();

        }





        if (lineCount % numChannel == 1) {
            istringstream iss(line);
           //peak
           int index_min = 0;
           int peak_min = 99999;
           double value;
           int nsp =0;
         while (iss >> value) {
           ADC[nsp] = value;
        Index_ADC[nsp] = nsp;
           //cout<<"T1:  "<<ADC[nsp]<<endl;
           //cout<<"T1index:  "<<Index_ADC[nsp]<<endl;
           nsp++;
           }

        for(int n=0; n< 1024; n++){
              if(peak_min>ADC[n] && n>420 && n<550){
            peak_min = ADC[n];
        //cout<<"T1 min:  "<<peak_min<<endl;
               index_min = Index_ADC[n];
              }
           }

           //baseline
           int GetbaseLine =1;
           if(GetbaseLine == 1){
              vector<int> rmsbase;

          int sum_baseLow = 0;
              int num_baseLow = 0;
              vector<int> rmsbaseLow;
              for(int kLow = 0; kLow < 100; kLow++){
           sum_baseLow += ADC[kLow];
                num_baseLow++;
        rmsbaseLow.push_back(ADC[kLow]);
              }
              double baseLow = sum_baseLow / num_baseLow;

              int sum_baseUp = 0;
              int num_baseUp = 0;
            vector<int> rmsbaseUp;
         for(int kUp = 300; kUp < 400; kUp++){
            sum_baseUp += ADC[kUp];
                num_baseUp++;
                rmsbaseUp.push_back(ADC[kUp]);
              }
              double baseUp = sum_baseUp / num_baseUp;

         if(baseLow>baseUp){
                 base = baseUp;
           rmsbase = rmsbaseUp;
           }
          else{
             base = baseLow;
            rmsbase = rmsbaseLow;
            }
              rmsbaseUp.clear();
              rmsbaseLow.clear();
///UP base//
              //rms
            rms = TMath::RMS(rmsbase.size(),&rmsbase[0]);
              rmsbase.clear();
      }
           //amp/overbase
           double sum_amp = 0;
           int count= 0;
           vector<int> overbase;
         for(int j = index_min - 50; j<index_min + 50; j++){
               sum_amp +=ADC[j];
       //cout<<"T2:   "<<sum_amp<<endl;
          count++;
               overbase.push_back(ADC[j]);
           }
           overshoot = (TMath::MaxElement(overbase.size(),&overbase[0]) - base) * (1/pow(2,12)) * 1000;
           overbase.clear();

         amp = (base - peak_min)* (1/pow(2,12))*1000;//U:mv
           //area2
           Index_minamp = index_min;
           Index_minamp2 = index_min;  // NEW: Save channel 1 peak position
           area2 = (count*base - sum_amp)*(1/pow(2,12))*1000/50 * 1;//Charge: pC

       //overshoot_Last
          double sum_amp_Last =0;
        vector<int> overbase_Last;
          for(int b = 800;b<1024;b++){
              //sum_amp_Last +=ADC[b];
             overbase_Last.push_back(ADC[b]);
          }
          overshoot_Last = (TMath::MaxElement(overbase_Last.size(),&overbase_Last[0]) - base) * (1/pow(2,12))*1000;
          overbase_Last.clear();
          //

        t1->Fill();

        }

//		t1->Fill();
	}

    TFile *fsave = new TFile("0000.root", "recreate");
    fsave->cd();
    t1->Write();
    fsave->Close();
    t1->Delete();
    fsave->Delete();
}
