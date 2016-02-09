TH2F *h1;
TH2F *h2;
TH1F *hcalo;

TTree *t1;
TTree *t2;
TTree *tcalo;

TCanvas *c1;
TCanvas *c2;

Int_t eventnr;
UInt_t nhits2;
UInt_t nhits1;

UShort_t *calo_data;
int size;

void event() {
	int event = gPad->GetEvent();
	if (event==kKeyPress) {
		int key = gPad->GetEventX();
		if (key == 'h') {
			if (eventnr>0) eventnr--;		
			viewtrack(eventnr);
		}
		else if(key=='l') {
			eventnr++;
			viewtrack(eventnr);
		}
		else if(key=='k') {
			do {
				if (eventnr++ >= t1->GetEntries()) { eventnr--; break; }
				t2->GetEntry(eventnr);
			} while (nhits2<1);
			viewtrack(eventnr);

		}
		else if(key=='j') {
			do {
				if (eventnr-- < 1) { eventnr++; break; }
				t2->GetEntry(eventnr);
			} while (nhits2<1);
			viewtrack(eventnr);

		}
		else if(key=='f') {
			do {
				if (eventnr-- < 1) { eventnr++; break; }
				t2->GetEntry(eventnr);
				t1->GetEntry(eventnr);
			} while ((nhits2<1) || (nhits1<1));
			viewtrack(eventnr);

		}
		else if(key=='g') {
			do {
				if (eventnr++ >= t1->GetEntries()) { eventnr--; break; }
				t2->GetEntry(eventnr);
				t1->GetEntry(eventnr);
			} while ((nhits2<1) || (nhits1<1));
			viewtrack(eventnr);

		}
	}
}
void viewtrack(Int_t nr) {
	h1->SetTitle(Form("Gridpix 1: %d",nr));
	h2->SetTitle(Form("Gridpix 2: %d",nr));
	c1->cd(1);
	t1->Draw("y:x>>h1","","",1,nr);
	c1->cd(2);
	t2->Draw("y:x>>h2","","",1,nr);
//	c1->cd(1);
//	h1->Draw();
//	c1->cd(2);
//	h2->Draw();
	c2->cd();
	hcalo->Clear();
	
	tcalo->GetEntry(nr);
	for (Int_t i=0;i<size;i++) {
		hcalo->SetBinContent(i,calo_data[i]);
	}
	hcalo->Draw();
	c1->Update();
	c2->Update();
}
void trackviewer(TString prefix,Int_t nStart=0) {
	eventnr = nStart;
	TString filename1 = prefix;
	TString filename2 = prefix;
	TString filenamecalo = prefix;
	filename1.Append("_1.root");
	filename2.Append("_2.root");
	filenamecalo.Append("_calo.root");

	c1 = new TCanvas("c1","c1");
	c2 = new TCanvas("c2","c2");
		
	TFile *f1 = new TFile(filename1);
	TFile *f2 = new TFile(filename2);
	fcalo = new TFile(filenamecalo);
	tcalo = (TTree *)fcalo->Get("calo");
	size = tcalo->GetLeaf("calo_data")->GetLen();
	calo_data = new UShort_t[size];
	tcalo->SetBranchAddress("calo_data",calo_data);
//	return 0;

	
	t1 = (TTree*)f1->Get("gridpix");
	t2 = (TTree*)f2->Get("gridpix");
	t2->SetBranchAddress("hits",&nhits2);
	t1->SetBranchAddress("hits",&nhits1);
	h1 = new TH2F("h1","h1",512,0,512,256,0,256);
	h2 = new TH2F("h2","h2",512,0,512,256,0,256);

	hcalo = new TH1F("hcalo","hcalo",size,0,size);
	h2->SetMarkerStyle(8);
	h2->SetMarkerSize(1);
	h1->SetMarkerStyle(8);
	h1->SetMarkerSize(1);
	gPad->AddExec("event","event()");
	c1->Divide(1,2);
	c1->cd(1);
	gPad->AddExec("event","event()");
	c1->cd(2);
	gPad->AddExec("event","event()");
	
	viewtrack(nStart);	
	

}
