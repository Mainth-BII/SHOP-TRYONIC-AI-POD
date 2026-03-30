import csv
from datetime import datetime
import os

class ReportWriter:
    """Writes test execution results to a CSV report."""

    def __init__(self, feature: str = "Chi-tiet-chuc-nang"):
        self.results = []
        date = datetime.now().strftime("%Y-%m-%d")
        self.report_path = f"RESULT_{feature}_{date}.csv"

    def add(self, tc_id: str, status: str, env: str = "Desktop Chrome", error: str = "", screenshot: str = "", actual_response: str = ""):
        self.results.append({
            "TC_ID": tc_id,
            "Environment": env,
            "Status": status,
            "Error_Message": error,
            "Screenshot_Path": screenshot,
            "Actual_Response": actual_response,
            "Executed_At": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    def save(self) -> str:
        headers = ["TC_ID", "Environment", "Status", "Error_Message", "Screenshot_Path", "Actual_Response", "Executed_At"]
        with open(self.report_path, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            writer.writerows(self.results)
        print(f"\n✅ Report saved: {self.report_path}")
        return self.report_path
