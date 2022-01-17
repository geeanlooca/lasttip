from setuptools import setup


with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="lasttip",
    version="1.0",
    description="A telegram bot to give a random album recommendation from my last.fm profile",
    author="Gianluca Marcon",
    author_email="marcon.gluca@gmail.com",
    packages=["lasttip"],
    install_requires=requirements,
    entry_points={"console_scripts": ["lasttip=lasttip.telegram_bot:main"]},
)
