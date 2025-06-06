from setuptools import setup, find_packages

setup(
    name="capsule-crm-mcp-server",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.68.0",
        "uvicorn>=0.15.0",
        "httpx>=0.24.0",
        "python-dotenv>=0.19.0",
        "pydantic>=1.8.0",
        "fastmcp>=0.1.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.18.0",
        ],
    },
    python_requires=">=3.8",
) 