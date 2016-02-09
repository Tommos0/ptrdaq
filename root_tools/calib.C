int max(unsigned short * const data, int const length) {
    int max=data[0];
    for (int i=1;i<length;i++)
        if (data[i]>max) max = data[i];
    return max;
}
int avg(unsigned short * const data, int const length) {
    int avg=0;
    for (int i=0;i<length;i++)
        avg+=data[i];
    return avg/length;
}
int calib() {
    int runs[11] = { 1,2,3,4,5,6,7,8,9,10,11 };
    Double_t energy[11] = { 150, 139.4, 130.1, 120.3, 110.6, 100.2, 90.8, 80.5, 71.0, 60.6,150 };
    TH1I * hist[11];
    //Fill the histograms
    for (Int_t i=0;i<11;i++) {
        TString filename = Form("/data/agor/run%d_calo.root",runs[i]);
        TString treename = "calo";
        hist[i] = new TH1I(Form("run%d",runs[i]),Form("run%d",runs[i]),100,0,2400);
        TFile *f = new TFile(filename);
        TTree *t = f->Get(treename);
        unsigned short calo_data[1602];
        t->SetBranchAddress("calo_data",calo_data);
        cout << treename << endl;
        for (int j=0;j<t->GetEntries();j++) {
            t->GetEntry(j);         
            hist[i]->Fill(max(calo_data,1602));
        }
        f->Close();
    }
    //Plot histograms
    gStyle->SetOptStat(0);
    TCanvas *c = new TCanvas("c","Energy Histogram",0,0,800,800);
    leg = new TLegend(0.1,0.7,0.48,0.9);
    c->cd();
    for (int i=0;i<11;i++) {
        if (i==10) hist[i]->SetFillColor(11);
        else hist[i]->SetFillColor(i+1);
        if (i==0) hist[i]->Draw();
        else hist[i]->Draw("SAME");
        leg->AddEntry(hist[i],Form("Run %d - %d MeV",runs[i],energy[i]),"f");
    }
   // leg->SetHeader("The Legend Title");
    leg->Draw();
    
    //Fit histograms -> plot energy calibration
    TCanvas *c2 = new TCanvas("c2","Energy Calibration",0,0,800,800);
    TGraph * g = new TGraph(11);
    for (int i=0;i<10;i++){
        //hist[i]->Fit("gaus","","",hist[i]->GetMean()-200,hist[i]->GetMean()+350);
        Double_t bincenter = hist[i]->GetBinCenter(hist[i]->GetMaximumBin());
        hist[i]->Fit("gaus","","",bincenter-100,bincenter+100);
        TF1 *f1 = hist[i]->GetFunction("gaus");
        g->SetPoint(i,f1->GetParameter(1),energy[i]);
    }
    g->Draw("A*");
    return 0;
}
