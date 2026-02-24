import asyncio
from flint.backends import get_all_backends

async def main():
    print("Testing backends...")
    backends = get_all_backends()
    print(f"Found {len(backends)} backends.")
    
    tasks = [b.list_models() for b in backends]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for backend, result in zip(backends, results):
        if isinstance(result, Exception):
            print(f"Backend {backend.name} failed: {result}")
        else:
            print(f"Backend {backend.name} returned {len(result)} models.")
            for m in result:
                print(f"  - {m.name}")

if __name__ == "__main__":
    asyncio.run(main()) 
