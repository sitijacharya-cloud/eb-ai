"""
Test MySQL Knowledge Base Retrieval
Verifies that retrieval works exactly like search_by_epic.py
"""

from backend.app.services.mysql_knowledge_base import get_knowledge_base

def test_retrieval():
    """Test the MySQL knowledge base retrieval"""
    print("\n" + "="*100)
    print("🧪 Testing MySQL Knowledge Base Retrieval")
    print("="*100)
    
    # Get knowledge base
    kb = get_knowledge_base()
    
    # Get stats
    print("\n📊 Knowledge Base Stats:")
    stats = kb.get_stats()
    print(f"   ✓ Total Epics: {stats['total_epics']}")
    print(f"   ✓ Total Templates: {stats['total_templates']}")
    print(f"   ✓ Sample Templates: {stats['templates'][:3]}")
    
    # Test queries
    test_queries = [
        ("authentication", 3),
        ("payment system", 2),
        ("database setup", 2),
    ]
    
    for query, n_results in test_queries:
        print(f"\n{'─'*100}")
        print(f"🔍 Query: '{query}' (top {n_results} results)")
        print(f"{'─'*100}")
        
        epics = kb.retrieve_similar_epics(query, n_results=n_results, similarity_threshold=0.3)
        
        if not epics:
            print("   ❌ No results found")
            continue
        
        print(f"\n✅ Found {len(epics)} epic(s)")
        
        for i, epic in enumerate(epics, 1):
            print(f"\n   📌 Epic #{i}: {epic.name}")
            print(f"      Source: {epic.source_template}")
            print(f"      Tasks: {len(epic.tasks)}")
            
            # Show sample tasks
            for j, task in enumerate(epic.tasks[:3], 1):
                print(f"         {j}. {task.description}")
                print(f"            Platforms: {list(task.efforts.keys())}")
                print(f"            Hours: {dict(task.efforts)}")
            
            if len(epic.tasks) > 3:
                print(f"         ... and {len(epic.tasks) - 3} more tasks")
    
    print("\n" + "="*100)
    print("✅ All tests completed!")
    print("="*100 + "\n")

if __name__ == "__main__":
    test_retrieval()
