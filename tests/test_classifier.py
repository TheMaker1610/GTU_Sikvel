"""
Тесты классификатора режимов ГТУ (на основе Приложения 2).
"""

import pytest
from server.analytics.classifier import ModeClassifier


@pytest.fixture
def classifier():
    return ModeClassifier()
