"""
Comparison Utilities for Estimation Coverage Analysis

This module provides functions to compare actual vs predicted estimations
focusing on coverage analysis (platforms, user roles, epics, tasks).
"""

from typing import Dict, List, Tuple, Set, Any
from difflib import SequenceMatcher
from collections import defaultdict
import re


def extract_user_type_from_epic_name(epic_name: str) -> str:
    """
    Extract user type from epic name.
    
    Epic names follow pattern: "Feature Name - UserType"
    Examples:
        "Portfolio Uploads - Photographer/Videographer" -> "Photographer/Videographer"
        "Personalised Content Feed -  Bride/Groom" -> "Bride/Groom"
        "Authentication" -> "Generic" (no user type)
    
    Args:
        epic_name: Epic name string
        
    Returns:
        User type string or "Generic" if no user type specified
    """
    # Match pattern: " - UserType" at end of string
    # Handle single or double spaces before dash
    match = re.search(r'\s+-\s+([A-Za-z/&\s]+)$', epic_name)
    if match:
        user_type = match.group(1).strip()
        # Normalize variations
        user_type = user_type.replace('&', '/').strip()
        return user_type
    return "Generic"


def fuzzy_match_string(str1: str, str2: str) -> float:
    """
    Calculate similarity ratio between two strings.
    
    Args:
        str1: First string
        str2: Second string
        
    Returns:
        Similarity score between 0.0 and 1.0
    """
    return SequenceMatcher(None, str1.lower().strip(), str2.lower().strip()).ratio()


def extract_platforms(estimation_data: Dict[str, Any]) -> Set[str]:
    """
    Extract all unique platforms from estimation data.
    
    Args:
        estimation_data: Parsed JSON estimation data
        
    Returns:
        Set of platform names (e.g., {'Flutter', 'API', 'CMS'})
    """
    platforms = set()
    
    epics = estimation_data.get('epics', [])
    
    # Handle old format: {"epics": {"Epic Name": {"Task": {"Platform": hours}}}}
    if isinstance(epics, dict):
        for epic_name, tasks in epics.items():
            if not isinstance(tasks, dict):
                continue
            for task_name, efforts in tasks.items():
                if isinstance(efforts, dict):
                    platforms.update(efforts.keys())
        return platforms
    
    # Handle new format: {"epics": [{"name": "", "tasks": [{"efforts": {}}]}]}
    if not isinstance(epics, list):
        return platforms
    
    for epic in epics:
        if not isinstance(epic, dict):
            continue
        tasks = epic.get('tasks', [])
        if not isinstance(tasks, list):
            continue
        for task in tasks:
            if not isinstance(task, dict):
                continue
            efforts = task.get('efforts', {})
            if isinstance(efforts, dict):
                platforms.update(efforts.keys())
    
    return platforms


def extract_user_roles(estimation_data: Dict[str, Any]) -> Set[str]:
    """
    Extract all unique user roles/types from estimation data.
    
    Args:
        estimation_data: Parsed JSON estimation data
        
    Returns:
        Set of user role names (e.g., {'Student', 'Teacher', 'Admin'})
    """
    user_roles = set()
    
    epics = estimation_data.get('epics', [])
    if not isinstance(epics, list):
        return user_roles
    
    for epic in epics:
        if not isinstance(epic, dict):
            continue
        epic_user_types = epic.get('user_types', [])
        if isinstance(epic_user_types, list):
            user_roles.update(epic_user_types)
        
        # Also check tasks (legacy format)
        tasks = epic.get('tasks', [])
        if not isinstance(tasks, list):
            continue
        for task in tasks:
            if not isinstance(task, dict):
                continue
            task_user_types = task.get('user_types', [])
            if isinstance(task_user_types, list):
                user_roles.update(task_user_types)
    
    return user_roles


def extract_epics(estimation_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Extract epic information from estimation data.
    
    Args:
        estimation_data: Parsed JSON estimation data
        
    Returns:
        List of epic dictionaries with name and task count
    """
    epics = []
    
    epic_list = estimation_data.get('epics', [])
    
    # Handle old format: {"epics": {"Epic Name": {"Task": {"Platform": hours}}}}
    if isinstance(epic_list, dict):
        for epic_name, tasks in epic_list.items():
            task_count = len(tasks) if isinstance(tasks, dict) else 0
            epics.append({
                'name': epic_name,
                'task_count': task_count,
                'user_types': [],
                'is_mandatory': False
            })
        return epics
    
    # Handle new format: {"epics": [{"name": "", "tasks": []}]}
    if not isinstance(epic_list, list):
        return epics
    
    for epic in epic_list:
        if not isinstance(epic, dict):
            continue
        
        tasks = epic.get('tasks', [])
        task_count = len(tasks) if isinstance(tasks, list) else 0
        
        user_types = epic.get('user_types', [])
        if not isinstance(user_types, list):
            user_types = []
        
        epics.append({
            'name': epic.get('name', epic.get('epic_name', 'Unknown')),
            'task_count': task_count,
            'user_types': user_types,
            'is_mandatory': epic.get('is_mandatory', False)
        })
    
    return epics


def calculate_total_hours(estimation_data: Dict[str, Any]) -> int:
    """
    Calculate total hours from estimation data.
    
    Args:
        estimation_data: Parsed JSON estimation data
        
    Returns:
        Total estimated hours
    """
    total = 0
    
    epics = estimation_data.get('epics', [])
    
    # Handle old format: {"epics": {"Epic Name": {"Task": {"Platform": hours}}}}
    if isinstance(epics, dict):
        for epic_name, tasks in epics.items():
            if not isinstance(tasks, dict):
                continue
            for task_name, efforts in tasks.items():
                if isinstance(efforts, dict):
                    total += sum(efforts.values())
        return total
    
    # Handle new format: {"epics": [{"tasks": [{"efforts": {}}]}]}
    if not isinstance(epics, list):
        return total
    
    for epic in epics:
        if not isinstance(epic, dict):
            continue
        tasks = epic.get('tasks', [])
        if not isinstance(tasks, list):
            continue
        for task in tasks:
            if not isinstance(task, dict):
                continue
            efforts = task.get('efforts', {})
            if isinstance(efforts, dict):
                total += sum(efforts.values())
    
    return total


def fuzzy_match_epics(
    actual_epics: List[Dict[str, Any]], 
    predicted_epics: List[Dict[str, Any]], 
    threshold: float = 0.6
) -> Tuple[List[Tuple], List[Dict], List[Dict]]:
    """
    Match epics between actual and predicted using fuzzy string matching.
    
    Args:
        actual_epics: List of actual epic dictionaries
        predicted_epics: List of predicted epic dictionaries
        threshold: Minimum similarity score for fuzzy match (0.0-1.0)
        
    Returns:
        Tuple of (matched, missing, extra):
        - matched: [(actual_epic, predicted_epic, similarity, match_type)]
        - missing: [actual epics not found in predicted]
        - extra: [predicted epics not found in actual]
    """
    matched = []
    missing = []
    extra = []
    
    actual_names = {epic['name']: epic for epic in actual_epics}
    predicted_names = {epic['name']: epic for epic in predicted_epics}
    
    used_predicted = set()
    
    # Phase 1: Exact matches (case-insensitive)
    for actual_name, actual_epic in actual_names.items():
        for predicted_name, predicted_epic in predicted_names.items():
            if predicted_name in used_predicted:
                continue
            
            if actual_name.lower().strip() == predicted_name.lower().strip():
                matched.append((actual_epic, predicted_epic, 1.0, 'EXACT'))
                used_predicted.add(predicted_name)
                break
    
    # Phase 2: Fuzzy matches
    matched_actual = {m[0]['name'] for m in matched}
    
    for actual_name, actual_epic in actual_names.items():
        if actual_name in matched_actual:
            continue
        
        best_match = None
        best_score = 0
        best_predicted_name = None
        
        for predicted_name, predicted_epic in predicted_names.items():
            if predicted_name in used_predicted:
                continue
            
            score = fuzzy_match_string(actual_name, predicted_name)
            if score >= threshold and score > best_score:
                best_score = score
                best_match = predicted_epic
                best_predicted_name = predicted_name
        
        if best_match:
            matched.append((actual_epic, best_match, best_score, 'FUZZY'))
            used_predicted.add(best_predicted_name)
    
    # Phase 3: Identify missing and extra
    matched_actual_names = {m[0]['name'] for m in matched}
    matched_predicted_names = {m[1]['name'] for m in matched}
    
    for actual_name, actual_epic in actual_names.items():
        if actual_name not in matched_actual_names:
            missing.append(actual_epic)
    
    for predicted_name, predicted_epic in predicted_names.items():
        if predicted_name not in matched_predicted_names:
            extra.append(predicted_epic)
    
    return matched, missing, extra


def compare_total_hours(actual_hours: int, predicted_hours: int) -> Dict[str, Any]:
    """
    Compare total hours between actual and predicted.
    
    Args:
        actual_hours: Total hours in actual estimation
        predicted_hours: Total hours in predicted estimation
        
    Returns:
        Dictionary with comparison results
    """
    difference = predicted_hours - actual_hours
    
    if actual_hours > 0:
        difference_percentage = (difference / actual_hours) * 100
    else:
        difference_percentage = 0
    
    if difference < 0:
        status = "UNDERESTIMATED"
    elif difference > 0:
        status = "OVERESTIMATED"
    else:
        status = "ACCURATE"
    
    return {
        'actual_hours': actual_hours,
        'predicted_hours': predicted_hours,
        'difference': difference,
        'difference_percentage': round(difference_percentage, 2),
        'status': status
    }


def compare_platforms(actual_platforms: Set[str], predicted_platforms: Set[str]) -> Dict[str, Any]:
    """
    Compare platform coverage between actual and predicted.
    
    Args:
        actual_platforms: Set of platforms in actual estimation
        predicted_platforms: Set of platforms in predicted estimation
        
    Returns:
        Dictionary with platform comparison results
    """
    matched = actual_platforms & predicted_platforms
    missing = actual_platforms - predicted_platforms
    extra = predicted_platforms - actual_platforms
    
    if len(actual_platforms) > 0:
        coverage_percentage = (len(matched) / len(actual_platforms)) * 100
    else:
        coverage_percentage = 0
    
    return {
        'total_actual': len(actual_platforms),
        'total_predicted': len(predicted_platforms),
        'matched_count': len(matched),
        'matched': sorted(list(matched)),
        'missing': sorted(list(missing)),
        'extra': sorted(list(extra)),
        'coverage_percentage': round(coverage_percentage, 2)
    }


def compare_user_roles(actual_roles: Set[str], predicted_roles: Set[str]) -> Dict[str, Any]:
    """
    Compare user role coverage between actual and predicted.
    
    Args:
        actual_roles: Set of user roles in actual estimation
        predicted_roles: Set of user roles in predicted estimation
        
    Returns:
        Dictionary with user role comparison results
    """
    matched = actual_roles & predicted_roles
    missing = actual_roles - predicted_roles
    extra = predicted_roles - actual_roles
    
    if len(actual_roles) > 0:
        coverage_percentage = (len(matched) / len(actual_roles)) * 100
    else:
        coverage_percentage = 0
    
    return {
        'total_actual': len(actual_roles),
        'total_predicted': len(predicted_roles),
        'matched_count': len(matched),
        'matched': sorted(list(matched)),
        'missing': sorted(list(missing)),
        'extra': sorted(list(extra)),
        'coverage_percentage': round(coverage_percentage, 2)
    }


def compare_epics(
    actual_epics: List[Dict[str, Any]], 
    predicted_epics: List[Dict[str, Any]],
    threshold: float = 0.6
) -> Dict[str, Any]:
    """
    Compare epic coverage between actual and predicted.
    
    Args:
        actual_epics: List of actual epic dictionaries
        predicted_epics: List of predicted epic dictionaries
        threshold: Fuzzy matching threshold
        
    Returns:
        Dictionary with epic comparison results
    """
    matched, missing, extra = fuzzy_match_epics(actual_epics, predicted_epics, threshold)
    
    exact_matches = [m for m in matched if m[3] == 'EXACT']
    fuzzy_matches = [m for m in matched if m[3] == 'FUZZY']
    
    if len(actual_epics) > 0:
        coverage_percentage = (len(matched) / len(actual_epics)) * 100
    else:
        coverage_percentage = 0
    
    return {
        'total_actual': len(actual_epics),
        'total_predicted': len(predicted_epics),
        'matched_count': len(matched),
        'exact_matches': len(exact_matches),
        'fuzzy_matches': len(fuzzy_matches),
        'missing_count': len(missing),
        'extra_count': len(extra),
        'matched': matched,
        'missing': missing,
        'extra': extra,
        'coverage_percentage': round(coverage_percentage, 2)
    }


def compare_tasks(
    actual_epics: List[Dict[str, Any]], 
    predicted_epics: List[Dict[str, Any]],
    matched_epics: List[Tuple]
) -> Dict[str, Any]:
    """
    Compare task coverage between actual and predicted.
    
    Args:
        actual_epics: List of actual epic dictionaries
        predicted_epics: List of predicted epic dictionaries
        matched_epics: List of matched epic tuples from compare_epics
        
    Returns:
        Dictionary with task comparison results
    """
    # Calculate average tasks per epic
    if len(actual_epics) > 0:
        avg_actual_tasks = sum(e['task_count'] for e in actual_epics) / len(actual_epics)
    else:
        avg_actual_tasks = 0
    
    if len(predicted_epics) > 0:
        avg_predicted_tasks = sum(e['task_count'] for e in predicted_epics) / len(predicted_epics)
    else:
        avg_predicted_tasks = 0
    
    # Epic-by-epic task comparison
    epic_task_details = []
    for actual_epic, predicted_epic, similarity, match_type in matched_epics:
        actual_count = actual_epic['task_count']
        predicted_count = predicted_epic['task_count']
        
        if actual_count > 0:
            coverage = (min(predicted_count, actual_count) / actual_count) * 100
        else:
            coverage = 100 if predicted_count == 0 else 0
        
        # Determine granularity
        if predicted_count < actual_count * 0.7:
            granularity = "LESS_GRANULAR"
        elif predicted_count > actual_count * 1.3:
            granularity = "MORE_GRANULAR"
        else:
            granularity = "SIMILAR"
        
        epic_task_details.append({
            'epic_name': actual_epic['name'],
            'actual_task_count': actual_count,
            'predicted_task_count': predicted_count,
            'coverage_percentage': round(coverage, 2),
            'granularity': granularity
        })
    
    # Overall task coverage
    if len(epic_task_details) > 0:
        overall_coverage = sum(d['coverage_percentage'] for d in epic_task_details) / len(epic_task_details)
    else:
        overall_coverage = 0
    
    # Granularity difference
    if avg_actual_tasks > 0:
        granularity_diff = ((avg_predicted_tasks - avg_actual_tasks) / avg_actual_tasks) * 100
    else:
        granularity_diff = 0
    
    return {
        'avg_actual_tasks': round(avg_actual_tasks, 2),
        'avg_predicted_tasks': round(avg_predicted_tasks, 2),
        'granularity_difference_percentage': round(granularity_diff, 2),
        'overall_task_coverage': round(overall_coverage, 2),
        'epic_task_details': epic_task_details
    }


def compare_epics_by_user_type(actual_epics: Dict[str, Any], predicted_epics: List[Dict[str, Any]], 
                               similarity_threshold: float = 60) -> Dict[str, Any]:
    """
    Compare epic coverage grouped by user type extracted from epic names.
    
    Args:
        actual_epics: Dictionary of actual epics {epic_name: epic_data}
        predicted_epics: List of predicted epics [{"name": "...", ...}]
        similarity_threshold: Threshold for fuzzy matching (0-100)
    
    Returns:
        Dictionary with per-user-type coverage statistics
    """
    from collections import defaultdict
    
    # Group actual epics by user type
    actual_by_user_type = defaultdict(list)
    for epic_name in actual_epics.keys():
        user_type = extract_user_type_from_epic_name(epic_name)
        actual_by_user_type[user_type].append(epic_name)
    
    # Group predicted epics by user type
    predicted_by_user_type = defaultdict(list)
    for epic in predicted_epics:
        epic_name = epic.get('name', '')
        user_type = extract_user_type_from_epic_name(epic_name)
        predicted_by_user_type[user_type].append(epic_name)
    
    # Get all unique user types
    all_user_types = sorted(set(list(actual_by_user_type.keys()) + list(predicted_by_user_type.keys())))
    
    # Calculate coverage for each user type
    user_type_coverage = {}
    for user_type in all_user_types:
        actual_user_epics = actual_by_user_type.get(user_type, [])
        predicted_user_epics = predicted_by_user_type.get(user_type, [])
        
        # Match epics within this user type using fuzzy matching
        matched = []
        missing = []
        
        for actual_epic in actual_user_epics:
            found_match = False
            for pred_epic in predicted_user_epics:
                # Convert similarity_threshold from 0-100 scale to 0-1 scale
                similarity_score = fuzzy_match_string(actual_epic, pred_epic)
                if similarity_score * 100 >= similarity_threshold:
                    matched.append({
                        'actual': actual_epic,
                        'predicted': pred_epic,
                        'similarity': similarity_score * 100
                    })
                    found_match = True
                    break
            
            if not found_match:
                missing.append(actual_epic)
        
        # Find extra epics in predicted but not in actual
        extra = []
        for pred_epic in predicted_user_epics:
            found_match = False
            for actual_epic in actual_user_epics:
                similarity_score = fuzzy_match_string(actual_epic, pred_epic)
                if similarity_score * 100 >= similarity_threshold:
                    found_match = True
                    break
            
            if not found_match:
                extra.append(pred_epic)
        
        total_actual = len(actual_user_epics)
        matched_count = len(matched)
        coverage = (matched_count / total_actual * 100) if total_actual > 0 else 0
        
        user_type_coverage[user_type] = {
            'total_actual': total_actual,
            'total_predicted': len(predicted_user_epics),
            'matched': matched_count,
            'missing': len(missing),
            'extra': len(extra),
            'coverage_percentage': round(coverage, 2),
            'matched_epics': matched,
            'missing_epics': missing,
            'extra_epics': extra
        }
    
    # Calculate overall statistics
    total_actual_all = sum(stats['total_actual'] for stats in user_type_coverage.values())
    total_matched_all = sum(stats['matched'] for stats in user_type_coverage.values())
    overall_coverage = (total_matched_all / total_actual_all * 100) if total_actual_all > 0 else 0
    
    return {
        'by_user_type': user_type_coverage,
        'overall_coverage': round(overall_coverage, 2),
        'total_user_types': len(all_user_types),
        'user_types': all_user_types
    }


def generate_status_emoji(coverage_percentage: float, good_threshold: float = 60, ok_threshold: float = 50) -> str:
    """
    Generate status emoji based on coverage percentage.
    
    Args:
        coverage_percentage: Coverage percentage (0-100)
        good_threshold: Threshold for "good" status (default 80%)
        ok_threshold: Threshold for "ok" status (default 50%)
        
    Returns:
        Status emoji string
    """
    if coverage_percentage >= good_threshold:
        return "✅"
    elif coverage_percentage >= ok_threshold:
        return "⚠️"
    else:
        return "❌"
