from setuptools import setup

setup(
    name="presque",
    entry_points={
        "spacy_factories": [
            "presque_normalizer = presque.normalizer:create_presque_normalizer"
        ]
    },
)
