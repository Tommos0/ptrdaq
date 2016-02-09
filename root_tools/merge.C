Int_t min3(Int_t a,Int_t b,Int_t c) {
    return TMath::Min(a,TMath::Min(b,c));
}
void merge(TString prefix,TString mergePrefix) {
    merge(prefix,mergePrefix,1,1,1);
}
void merge(char* prefix,char* mergePrefix,Int_t skip1, Int_t skip2, Int_t skipcalo) {
    TFile *fgp1 = new TFile(Form("%s_1.root",prefix),"read");
    TFile *fgp2 = new TFile(Form("%s_2.root",prefix),"read");
    TFile *fcalo = new TFile(Form("%s_calo.root",prefix),"read");
    TFile *fmerge = new TFile(Form("%s.root",mergePrefix),"recreate");
    TTree *tmerge = new TTree("data","data");

    TTree *tgp1 = fgp1->Get("gridpix");
    TTree *tgp2 = fgp2->Get("gridpix");
    TTree *tcalo = fcalo->Get("calo");
    unsigned short x1[512*256],y1[512*256],z1[512*256],x2[512*256],y2[512*256],z2[512*256];
    unsigned int hits1,hits2,time1,time2,timecalo;
    int len = tcalo->GetLeaf("calo_data")->GetLen();
    cout << "len" << len << endl;
    //unsigned short *calo_data = new unsigned short[len];
    unsigned short calo_data[1602];
    tgp1->SetBranchAddress("hits",&hits1);
    tgp1->SetBranchAddress("x",x1);
    tgp1->SetBranchAddress("y",y1);
    tgp1->SetBranchAddress("z",z1);
    tgp1->SetBranchAddress("time",&time1);
    tgp2->SetBranchAddress("hits",&hits2);
    tgp2->SetBranchAddress("x",x2);
    tgp2->SetBranchAddress("y",y2);
    tgp2->SetBranchAddress("z",z2);
    tgp2->SetBranchAddress("time",&time2);
    tcalo->SetBranchAddress("calo_data",calo_data);
    tcalo->SetBranchAddress("time",&timecalo);

    tmerge->Branch("cam1_hits",&hits1,"cam1_hits/i");
    tmerge->Branch("cam1_x",&x1,"cam1_x[cam1_hits]/s");
    tmerge->Branch("cam1_y",&y1,"cam1_y[cam1_hits]/s");
    tmerge->Branch("cam1_z",&z1,"cam1_z[cam1_hits]/s");
    tmerge->Branch("cam1_time",&time1,"cam1_time/i");

    tmerge->Branch("cam2_hits",&hits2,"cam2_hits/i");
    tmerge->Branch("cam2_x",&x2,"cam2_x[cam2_hits]/s");
    tmerge->Branch("cam2_y",&y2,"cam2_y[cam2_hits]/s");
    tmerge->Branch("cam2_z",&z2,"cam2_z[cam2_hits]/s");
    tmerge->Branch("cam2_time",&time2,"cam2_time/i");

    tmerge->Branch("calo_data",&calo_data,Form("calo_data[%i]/s",len));
    tmerge->Branch("calo_time",&timecalo,"calo_time/i");

    Int_t ev1 = tgp1->GetEntries()-skip1;
    Int_t ev2 = tgp2->GetEntries()-skip2;
    Int_t evcalo = tcalo->GetEntries()-skipcalo;

    for (Int_t i=0;i<min3(ev1,ev2,evcalo);i++){
        tgp1->GetEntry(i+skip1);
        tgp2->GetEntry(i+skip2);
        tcalo->GetEntry(i+skipcalo);
        tmerge->Fill();
//	cout << i << endl;
    }
    fgp1->Close();
    fgp2->Close();
    fcalo->Close();
    fmerge->Write();
    fmerge->Close();
}
