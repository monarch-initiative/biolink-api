from ontobio.golr.golr_sim import subject_pair_simj

gene_ids= [
"NCBIGene:10891",
"NCBIGene:11067",
"NCBIGene:1118",
"NCBIGene:1174",
"NCBIGene:12",
"NCBIGene:1200",
"NCBIGene:1201",
"NCBIGene:1203",
"NCBIGene:123",
    ]

categs = ['phenotype', 'gene', 'disease', 'function']
def test_sim():
    for i in gene_ids:
        for j in gene_ids:
            
            if i <= j:
                continue
            for k in categs:
                print("Comparing: "+i+" "+j+" using "+k)
                results = subject_pair_simj(subject1=i,
                                            subject2=j,
                                            object_category=k)
                print(str(results))
    assert False is True
