# sample_data_generator.py
# Generate sample data for testing the Smart Sprayer GUI

import sys
import os
from datetime import datetime, timedelta
import random

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from core.data_store import get_data_store
from core.logger import get_logger


def generate_sample_schedules():
    """Generate sample schedules for testing"""
    data_store = get_data_store()
    logger = get_logger()
    
    print("=" * 60)
    print("SAMPLE DATA GENERATOR")
    print("=" * 60)
    print("\nGenerating sample schedules...\n")
    
    # Clear existing schedules
    data_store.clear_all_schedules()
    
    # Generate schedules starting from tomorrow
    start_date = datetime.now() + timedelta(days=1)
    
    schedules = []
    
    # Schedule 1: Fertilizer tomorrow
    schedule1 = {
        'date': start_date.strftime('%Y-%m-%d'),
        'time': '08:00',
        'spray_type': 'Fertilizer',
        'container': 'Container 1',
        'duration': 30,
        'status': 'scheduled'
    }
    schedules.append(data_store.add_schedule(schedule1))
    print(f"✓ Created: {schedule1['date']} - {schedule1['spray_type']}")
    
    # Schedule 2: Pesticide day after tomorrow
    schedule2 = {
        'date': (start_date + timedelta(days=1)).strftime('%Y-%m-%d'),
        'time': '09:30',
        'spray_type': 'Pesticide',
        'container': 'Container 2',
        'duration': 25,
        'status': 'scheduled'
    }
    schedules.append(data_store.add_schedule(schedule2))
    print(f"✓ Created: {schedule2['date']} - {schedule2['spray_type']}")
    
    # Schedule 3: Recurring series (every 7 days, 3 times)
    series_id = f"SERIES_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    for i in range(3):
        schedule_date = (start_date + timedelta(days=3 + i*7)).strftime('%Y-%m-%d')
        schedule = {
            'date': schedule_date,
            'time': '07:00',
            'spray_type': 'Fertilizer',
            'container': 'Container 1',
            'duration': 30,
            'status': 'scheduled',
            'series_id': series_id,
            'series_interval': 7
        }
        schedules.append(data_store.add_schedule(schedule))
        print(f"✓ Created: {schedule['date']} - {schedule['spray_type']} (Series)")
    
    print(f"\n✓ Total schedules created: {len(schedules)}")
    logger.log_info(f"Sample schedules generated: {len(schedules)}")
    
    return schedules


def generate_sample_history():
    """Generate sample spray history"""
    data_store = get_data_store()
    logger = get_logger()
    
    print("\nGenerating sample history...\n")
    
    # Clear existing history
    data_store.clear_history()
    
    # Generate history for past 10 days
    spray_types = ['Fertilizer', 'Pesticide']
    containers = ['Container 1', 'Container 2']
    
    for i in range(10, 0, -1):
        spray_date = datetime.now() - timedelta(days=i)
        
        history_item = {
            'date': spray_date.strftime('%Y-%m-%d'),
            'time': f"{random.randint(7, 10):02d}:{random.choice(['00', '30'])}",
            'spray_type': random.choice(spray_types),
            'container': random.choice(containers),
            'duration': random.randint(25, 35),
            'schedule_id': f"HIST_{i:03d}",
            'completed_at': spray_date.isoformat()
        }
        
        data_store.add_to_history(history_item)
        print(f"✓ Added history: {history_item['date']} - {history_item['spray_type']}")
    
    print(f"\n✓ Total history entries: 10")
    logger.log_info("Sample history generated: 10 entries")


def main():
    """Main entry point"""
    try:
        # Generate schedules
        schedules = generate_sample_schedules()
        
        # Generate history
        generate_sample_history()
        
        print("\n" + "=" * 60)
        print("SAMPLE DATA GENERATION COMPLETE")
        print("=" * 60)
        print("\nYou can now run the GUI to see the sample data:")
        print("  python run_gui.py")
        print("\nSample data includes:")
        print(f"  • {len(schedules)} scheduled sprays")
        print("  • 10 historical spray records")
        print("  • Various spray types and containers")
        print("  • Recurring schedule series")
        print("\n" + "=" * 60)
    
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
