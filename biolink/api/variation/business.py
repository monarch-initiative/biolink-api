from biolink.database import db
from biolink.database.models import VariantSet, Category


def create_variantset(data):
    title = data.get('title')
    body = data.get('body')
    category_id = data.get('category_id')
    category = Category.query.filter(Category.id == category_id).one()
    variantset = Variantset(title, body, category)
    db.session.add(variantset)
    db.session.commit()


def update_variantset(variantset_id, data):
    variantset = Variantset.query.filter(Variantset.id == variantset_id).one()
    variantset.title = data.get('title')
    variantset.body = data.get('body')
    category_id = data.get('category_id')
    variantset.category = Category.query.filter(Category.id == category_id).one()
    db.session.add(variantset)
    db.session.commit()


def delete_variantset(variantset_id):
    variantset = Variantset.query.filter(Variantset.id == variantset_id).one()
    db.session.delete(variantset)
    db.session.commit()


def create_category(data):
    name = data.get('name')
    category_id = data.get('id')

    category = Category(name)
    if category_id:
        category.id = category_id

    db.session.add(category)
    db.session.commit()


def update_category(category_id, data):
    category = Category.query.filter(Category.id == category_id).one()
    category.name = data.get('name')
    db.session.add(category)
    db.session.commit()


def delete_category(category_id):
    category = Category.query.filter(Category.id == category_id).one()
    db.session.delete(category)
    db.session.commit()
