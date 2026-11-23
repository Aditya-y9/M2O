"""
Automated Migration Plan Generator with AI-Powered Wave Planning
Generates phased roadmap with team assignments, critical path, and timelines
"""
from typing import Dict, List, Any
from datetime import datetime, timedelta


class MigrationPlanGenerator:
    """Generate comprehensive migration plans from assessment data."""
    
    def __init__(self):
        self.effort_rates = {
            "program": 5,      # days per program
            "data_store": 8,   # days per database
            "transaction": 3,  # days per transaction
            "job": 4,          # days per batch job
            "interface": 2     # days per interface
        }
        
    def generate_plan(self, report_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate comprehensive migration plan from assessment data.
        
        Returns:
            Dictionary with phases, waves, tasks, timeline, resources
        """
        portfolio = report_data.get("portfolio", {})
        graph = report_data.get("dependency_graph", {})
        assessment = report_data.get("assessment_report", {})
        
        # Build dependency graph
        nodes = {n.get("id"): n for n in graph.get("nodes", [])}
        edges = graph.get("edges", [])
        
        # Calculate in/out degrees
        in_degrees = {}
        out_degrees = {}
        for edge in edges:
            source = edge.get("source")
            target = edge.get("target")
            in_degrees[target] = in_degrees.get(target, 0) + 1
            out_degrees[source] = out_degrees.get(source, 0) + 1
        
        # Identify critical components (high dependencies)
        critical_components = []
        for node_id, node in nodes.items():
            risk_score = in_degrees.get(node_id, 0) * 2 + out_degrees.get(node_id, 0)
            if risk_score > 10:
                critical_components.append({
                    "id": node_id,
                    "name": node.get("name", "Unknown"),
                    "type": node.get("type", "unknown"),
                    "risk_score": risk_score,
                    "in_degree": in_degrees.get(node_id, 0),
                    "out_degree": out_degrees.get(node_id, 0)
                })
        
        # Sort by dependencies (foundation first)
        critical_components.sort(key=lambda c: c["out_degree"], reverse=True)
        
        # Generate 3-phase plan
        phases = self._generate_phases(portfolio, critical_components, nodes, edges)
        
        # Calculate timeline
        timeline = self._calculate_timeline(phases)
        
        # Identify critical path
        critical_path = self._identify_critical_path(phases)
        
        # Generate resource plan
        resource_plan = self._generate_resource_plan(phases)
        
        return {
            "phases": phases,
            "timeline": timeline,
            "critical_path": critical_path,
            "resource_plan": resource_plan,
            "summary": {
                "total_duration_days": timeline["total_days"],
                "total_effort_days": sum(p["effort_days"] for p in phases),
                "recommended_team_size": resource_plan["recommended_team_size"],
                "critical_components": len(critical_components),
                "total_components": len(nodes)
            }
        }
    
    def _generate_phases(
        self,
        portfolio: Dict[str, Any],
        critical_components: List[Dict],
        nodes: Dict[str, Any],
        edges: List[Dict]
    ) -> List[Dict[str, Any]]:
        """Generate 3-phase migration plan."""
        
        # Phase 1: Foundation - Data & Infrastructure
        foundation_tasks = []
        for ds in portfolio.get("data_stores", []):
            foundation_tasks.append({
                "id": f"migrate_{ds.get('id', '')}",
                "name": f"Migrate {ds.get('name', 'Database')}",
                "type": "data_migration",
                "component_type": "data_store",
                "effort_days": self.effort_rates["data_store"],
                "priority": "critical",
                "dependencies": []
            })
        
        # Phase 2: Core Logic - Programs & Batch Jobs
        core_tasks = []
        for prog in portfolio.get("programs", []):
            # Check if this is a critical component
            is_critical = any(c["id"] == prog.get("id") for c in critical_components)
            
            core_tasks.append({
                "id": f"migrate_{prog.get('id', '')}",
                "name": f"Migrate {prog.get('name', 'Program')}",
                "type": "code_migration",
                "component_type": "program",
                "effort_days": self.effort_rates["program"],
                "priority": "critical" if is_critical else "high",
                "dependencies": ["phase_1_complete"]
            })
        
        for job in portfolio.get("jobs", []):
            core_tasks.append({
                "id": f"migrate_{job.get('id', '')}",
                "name": f"Migrate {job.get('name', 'Batch Job')}",
                "type": "batch_migration",
                "component_type": "job",
                "effort_days": self.effort_rates["job"],
                "priority": "high",
                "dependencies": ["phase_1_complete"]
            })
        
        # Phase 3: Integration - Transactions & Interfaces
        integration_tasks = []
        for txn in portfolio.get("transactions", []):
            integration_tasks.append({
                "id": f"migrate_{txn.get('id', '')}",
                "name": f"Migrate {txn.get('name', 'Transaction')}",
                "type": "transaction_migration",
                "component_type": "transaction",
                "effort_days": self.effort_rates["transaction"],
                "priority": "high",
                "dependencies": ["phase_2_complete"]
            })
        
        # Add testing tasks to each phase
        foundation_tasks.append({
            "id": "phase_1_testing",
            "name": "Foundation Testing & Validation",
            "type": "testing",
            "component_type": "test",
            "effort_days": 10,
            "priority": "critical",
            "dependencies": [t["id"] for t in foundation_tasks if t.get("type") != "testing"]
        })
        
        core_tasks.append({
            "id": "phase_2_testing",
            "name": "Core Logic Testing & Validation",
            "type": "testing",
            "component_type": "test",
            "effort_days": 15,
            "priority": "critical",
            "dependencies": [t["id"] for t in core_tasks if t.get("type") != "testing"]
        })
        
        integration_tasks.append({
            "id": "phase_3_testing",
            "name": "End-to-End Integration Testing",
            "type": "testing",
            "component_type": "test",
            "effort_days": 20,
            "priority": "critical",
            "dependencies": [t["id"] for t in integration_tasks if t.get("type") != "testing"]
        })
        
        return [
            {
                "phase_number": 1,
                "name": "Foundation: Data & Infrastructure",
                "description": "Migrate data stores and establish cloud infrastructure",
                "tasks": foundation_tasks,
                "effort_days": sum(t["effort_days"] for t in foundation_tasks),
                "parallel_tracks": 2
            },
            {
                "phase_number": 2,
                "name": "Core Logic: Programs & Batch",
                "description": "Migrate business logic programs and batch jobs",
                "tasks": core_tasks,
                "effort_days": sum(t["effort_days"] for t in core_tasks),
                "parallel_tracks": 3
            },
            {
                "phase_number": 3,
                "name": "Integration: Transactions & UI",
                "description": "Migrate online transactions and integrate all components",
                "tasks": integration_tasks,
                "effort_days": sum(t["effort_days"] for t in integration_tasks),
                "parallel_tracks": 2
            }
        ]
    
    def _calculate_timeline(self, phases: List[Dict]) -> Dict[str, Any]:
        """Calculate project timeline with parallel execution."""
        start_date = datetime.now()
        current_date = start_date
        phase_timelines = []
        
        for phase in phases:
            # Calculate duration with parallel execution
            parallel_tracks = phase.get("parallel_tracks", 1)
            total_effort = phase["effort_days"]
            duration_days = total_effort / parallel_tracks
            
            phase_start = current_date
            phase_end = current_date + timedelta(days=duration_days)
            
            phase_timelines.append({
                "phase": phase["phase_number"],
                "name": phase["name"],
                "start_date": phase_start.strftime("%Y-%m-%d"),
                "end_date": phase_end.strftime("%Y-%m-%d"),
                "duration_days": duration_days,
                "effort_days": total_effort
            })
            
            current_date = phase_end
        
        return {
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": current_date.strftime("%Y-%m-%d"),
            "total_days": (current_date - start_date).days,
            "phases": phase_timelines
        }
    
    def _identify_critical_path(self, phases: List[Dict]) -> List[Dict[str, Any]]:
        """Identify critical path tasks that block overall completion."""
        critical_path = []
        
        for phase in phases:
            # Find critical tasks (testing and high-priority items)
            critical_tasks = [
                t for t in phase["tasks"]
                if t.get("priority") == "critical" or t.get("type") == "testing"
            ]
            
            for task in critical_tasks:
                critical_path.append({
                    "phase": phase["phase_number"],
                    "task_id": task["id"],
                    "task_name": task["name"],
                    "effort_days": task["effort_days"],
                    "blocks": "Phase completion" if task.get("type") == "testing" else "Dependent tasks"
                })
        
        return critical_path
    
    def _generate_resource_plan(self, phases: List[Dict]) -> Dict[str, Any]:
        """Generate resource allocation plan."""
        total_effort = sum(p["effort_days"] for p in phases)
        max_parallel = max(p.get("parallel_tracks", 1) for p in phases)
        
        # Calculate team composition
        team_roles = {
            "Migration Architect": 1,
            "Backend Developers": max(2, max_parallel - 1),
            "Data Engineers": 2,
            "QA Engineers": 2,
            "DevOps Engineer": 1
        }
        
        recommended_team_size = sum(team_roles.values())
        
        return {
            "recommended_team_size": recommended_team_size,
            "team_composition": team_roles,
            "estimated_cost": {
                "blended_rate_per_day": 800,
                "total_labor_cost": total_effort * 800,
                "contingency_20_percent": total_effort * 800 * 0.2
            },
            "skill_requirements": [
                "COBOL to Java/Python conversion",
                "Cloud infrastructure (AWS/Azure/GCP)",
                "Database migration (DB2/IMS to PostgreSQL/MongoDB)",
                "Container orchestration (Kubernetes/OpenShift)",
                "CI/CD pipeline setup",
                "Mainframe domain knowledge"
            ]
        }


def format_migration_plan_html(plan: Dict[str, Any]) -> str:
    """Format migration plan as HTML for display."""
    
    summary = plan["summary"]
    timeline = plan["timeline"]
    
    html = f"""
    <div style="font-family: sans-serif; padding: 20px; background: #f5f5f5;">
        <h1 style="color: #333;">📋 Automated Migration Plan</h1>
        
        <div style="background: white; padding: 20px; margin: 20px 0; border-radius: 8px;">
            <h2>Executive Summary</h2>
            <ul>
                <li><strong>Total Duration:</strong> {summary['total_duration_days']} days ({summary['total_duration_days'] / 30:.1f} months)</li>
                <li><strong>Total Effort:</strong> {summary['total_effort_days']} person-days</li>
                <li><strong>Recommended Team:</strong> {summary['recommended_team_size']} people</li>
                <li><strong>Components:</strong> {summary['critical_components']} critical / {summary['total_components']} total</li>
            </ul>
        </div>
        
        <div style="background: white; padding: 20px; margin: 20px 0; border-radius: 8px;">
            <h2>Timeline</h2>
            <p><strong>Start:</strong> {timeline['start_date']} | <strong>End:</strong> {timeline['end_date']}</p>
            
            <table style="width: 100%; border-collapse: collapse; margin-top: 10px;">
                <thead>
                    <tr style="background: #e3e3e3;">
                        <th style="padding: 10px; text-align: left;">Phase</th>
                        <th style="padding: 10px; text-align: left;">Start</th>
                        <th style="padding: 10px; text-align: left;">End</th>
                        <th style="padding: 10px; text-align: right;">Duration</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    for phase_timeline in timeline["phases"]:
        html += f"""
                    <tr style="border-bottom: 1px solid #ddd;">
                        <td style="padding: 10px;">{phase_timeline['name']}</td>
                        <td style="padding: 10px;">{phase_timeline['start_date']}</td>
                        <td style="padding: 10px;">{phase_timeline['end_date']}</td>
                        <td style="padding: 10px; text-align: right;">{phase_timeline['duration_days']:.0f} days</td>
                    </tr>
        """
    
    html += """
                </tbody>
            </table>
        </div>
        
        <div style="background: white; padding: 20px; margin: 20px 0; border-radius: 8px;">
            <h2>Critical Path</h2>
            <p>Tasks that block overall completion:</p>
            <ul>
    """
    
    for task in plan["critical_path"]:
        html += f"""
                <li><strong>Phase {task['phase']}:</strong> {task['task_name']} ({task['effort_days']} days) - {task['blocks']}</li>
        """
    
    html += """
            </ul>
        </div>
    </div>
    """
    
    return html
