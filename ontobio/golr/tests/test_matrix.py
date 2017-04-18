from ontobio.golr.golr_matrix import term_matrix


idlist=[
    'HP:0000021', ## Megacystis
    'HP:0000024', ## Prostatitis
    'HP:0000026', ## Male hypogonadism
    'HP:0000028', ## Cryptorchidism
    'HP:0000096', ## Glomerulosclerosis
    'HP:0000068', ## Urethral atresia
]

def test_matrix():
    results = term_matrix(idlist=idlist,
                          subject_category='gene',
                          taxon='NCBITaxon:9606')
    print(str(results))
