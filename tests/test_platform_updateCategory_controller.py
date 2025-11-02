import pytest
from app import create_app, db
from app.entity.category import Category
from app.control.platform_updateCategory_controller import PlatformUpdateCategoryController

@pytest.fixture()
def app():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })
    with app.app_context():
        db.create_all()

        # Create dummy category
        category = Category(categoryName="Old Name", description="Old description")
        db.session.add(category)
        db.session.commit()

    yield app


def test_update_category_success(app):
    """Ensure updateCategory() updates category correctly."""
    with app.app_context():
        controller = PlatformUpdateCategoryController()

        category = Category.query.first()
        result = controller.updateCategory(category.categoryID, "New Name", "New description")

        updated = Category.query.get(category.categoryID)

        assert result is True
        assert updated.categoryName == "New Name"
        assert updated.description == "New description"


def test_update_category_not_found(app):
    """Ensure ValueError is raised when category not found."""
    with app.app_context():
        controller = PlatformUpdateCategoryController()
        with pytest.raises(ValueError):
            controller.updateCategory(9999, "Doesn't exist", "No category here")
