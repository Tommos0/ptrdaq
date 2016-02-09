TH3F *h1;
TH3F *h2;
TTree *t1;
TTree *t2;
TCanvas *c1;
Int_t eventnr;
UInt_t nhits2;
UInt_t nhits1;
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
	t1->Draw("z:y:x>>h1","","",1,nr);
	c1->cd(2);
	t2->Draw("z:y:x>>h2","","",1,nr);
//	c1->cd(1);
//	h1->Draw();
//	c1->cd(2);
//	h2->Draw();
	c1->Update();
}
void trackviewer3d(TString prefix,Int_t nStart=0) {
	eventnr = nStart;
	TString filename1 = prefix;
	TString filename2 = prefix;
	filename1.Append("_1.root");
	filename2.Append("_2.root");
	c1 = new TCanvas("c1","c1");
		
	TFile *f1 = new TFile(filename1);
	TFile *f2 = new TFile(filename2);
	
	t1 = (TTree*)f1->Get("gridpix");
	t2 = (TTree*)f2->Get("gridpix");
	t2->SetBranchAddress("hits",&nhits2);
	t1->SetBranchAddress("hits",&nhits1);
	h1 = new TH3F("h1","h1",512,0,512,256,0,256,200,0,200);
	h2 = new TH3F("h2","h2",512,0,512,256,0,256,200,0,200);
//
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
