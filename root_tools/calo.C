TFile *f;
TTree *t;
UShort_t *calo_data;
int size;

void plot(Int_t nr) {
	t->GetEntry(nr);
	TH1F * dist = new TH1F("dist","dist",size,0,size);
	cout << size << endl;
	for (Int_t i=0;i<size;i++) {
		dist->SetBinContent(i,calo_data[i]);
	}
	dist->Draw();

}
int calo() {
	f = new TFile("/data/agor/test11_calo.root");
	t = (TTree *)f->Get("calo");
	size = t->GetLeaf("calo_data")->GetLen();
	cout << size << endl;
	calo_data = new UShort_t[size];
	t->SetBranchAddress("calo_data",calo_data);
	return 0;

}
