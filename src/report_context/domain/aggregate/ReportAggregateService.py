from src.report_context.infrastructure.repositories.ReportRepository import ReportRepository
from src.report_context.infrastructure.repositories.NotificationRepository import NotificationRepository
from src.register_context.infrastructure.repositories.UserRepository import UserRepository
from src.register_context.infrastructure.repositories.AdminRepository import AdminRepository
from src.search_context.infrastructure.repositories.ChargingStationRepository import ChargingStationRepository
from src.report_context.domain.events.ReportAlreadyExistsEvent import ReportAlreadyExistsEvent  
from src.report_context.domain.entities.report import Report
from src.report_context.domain.events.ReportCreateFailedEvent import ReportCreateFailedEvent
from src.report_context.domain.events.ReportCreateEvent import ReportCreateEvent
from src.register_context.infrastructure.repositories.CSOperatorRepository import CSOperatorRepository
from typing import Union
from src.report_context.domain.events.ReportUpdateEvent import ReportUpdateEvent

class ReportAggregateService:
    def __init__(self, report_repository: ReportRepository, user_repository: UserRepository, notification_repository: NotificationRepository, admin_repository: AdminRepository, chargingstation_repository: ChargingStationRepository, csoperator_repository: CSOperatorRepository):
        self.report_repository = report_repository
        self.user_repository = user_repository
        self.notification_repository = notification_repository
        self.admin_repository = admin_repository
        self.chargingstation_repository = chargingstation_repository
        self.csoperator_repository = csoperator_repository
        self.events = []
        
    def get_events(self):
        return self.events

    def report_malfunction(self, report: Report) -> Union[ReportAlreadyExistsEvent, ReportCreateFailedEvent, ReportCreateEvent]:
        all_admins = self.admin_repository.get_all_admins()
        admin = None
        for admin in all_admins:
            if(admin.number_reports_assigned < 10):
                admin = admin
                break
        # If no admin with less than 10 reports is found, get the first admin
        if not admin:
            admin = all_admins[0]
            
        report.admin_id = admin.sys_admin_id
        
        exisiting_reports = self.report_repository.find_reports_by_station_id(report.station_id)
    
        for exisiting_report in exisiting_reports:
            if exisiting_report is not None and exisiting_report.status != "resolved":
                event = ReportAlreadyExistsEvent(exisiting_report, "Malfunction report has already been forwarded for this station")
                self.events.append(("REPORT MALFUNCTION", event))
                return event

        success = self.report_repository.create_report(report)
        
        if not success:
            event = ReportCreateFailedEvent("Report creation failed")
            self.events.append(("REPORT MALFUNCTION", event))
            return event
        
        # Update the number of reports assigned to the admin
        admin.number_reports_assigned += 1
        self.admin_repository.update_admin(admin)
        
        # Change status of station to "out_of_service"
        self.chargingstation_repository.update_charging_station(report.station_id, "out_of_service")
        
        # Send notification to users
        all_users = self.user_repository.get_all_users()
        self.notification_repository.create_notifications([user.user_id for user in all_users], f"""<h5>MALFUNCTION HAS BEEN REPORTED FOR STATION ID: {report.station_id}</h5>
            <ul>
                <li>Street: {report.chargingstation.street}</li>
                <li>Postal Code: {report.chargingstation.postal_code}</li>
                <li>District: {report.chargingstation.district}</li>
            </ul>
            <strong>Please check nearby charging stations for alternative options while this issue is addressed. Thank you for your cooperation.</strong>""")
        
        event = ReportCreateEvent(True)
        self.events.append(("REPORT MALFUNCTION", event))
        return event
       
    def forward_report_malfunction(self, report: Report) -> Union[ReportUpdateEvent, ValueError]:
        try: 
            all_csoperators = self.csoperator_repository.get_all_csoperators()
            cs_operator = None
            # Get the first operator with less than 10 reports assigned
            for operator in all_csoperators:
                if(operator.number_reports_assigned < 10):
                    cs_operator = operator
                    break
            # If no operator with less than 10 reports is found, get the first operator
            if not cs_operator:
                cs_operator = all_csoperators[0]
            
            # Update the report
            report.csoperator = cs_operator
            report.status = "managed"
            updated_report = self.report_repository.update_report(report)
            
            # report_service.update_report(report)
            
            # Update the charging station operator
            cs_operator.number_reports_assigned += 1
            self.csoperator_repository.update_csoperator(cs_operator)
            
            event = ReportUpdateEvent(updated_report)
            self.events.append(("FORWARD REPORT MALFUNCTION", event))
            return event
        except (TypeError, ValueError) as e:
            event = ValueError(e)
            self.events.append(("FORWARD REPORT MALFUNCTION", event))
            return e
        
    def resolve_report_malfunction(self, report: Report) -> Union[ReportUpdateEvent, ValueError]:
        try: 
            # Update the admin
            admin = report.admin
            admin.number_reports_assigned -= 1
            self.admin_repository.update_admin(admin)
            
            # Update the charging station operator
            cs_operator = report.csoperator
            cs_operator.number_reports_assigned -= 1
            self.csoperator_repository.update_csoperator(cs_operator)
            
            # Change status of station
            self.chargingstation_repository.update_charging_station(report.station_id, "available")
            
            # Send notification to users
            all_users = self.user_repository.get_all_users()
            self.notification_repository.create_notifications([user.user_id for user in all_users], f"""<h5>ISSUE RESOLVED FOR STATION ID: {report.station_id}</h5>
                <ul>
                    <li>Street: {report.chargingstation.street}</li>
                    <li>Postal Code: {report.chargingstation.postal_code}</li>
                    <li>District: {report.chargingstation.district}</li>
                </ul>
                <strong>The reported malfunction has been resolved, and the charging station is now fully operational. Thank you for your patience and cooperation..</strong>""")
            
            # Update the report
            report.status = "resolved"
            updated_report = self.report_repository.update_report(report)
            
            event = ReportUpdateEvent(updated_report)
            self.events.append(("RESOLVE REPORT MALFUNCTION", event))
            return event
        
        except (TypeError, ValueError) as e:
            event = ValueError(e)
            self.events.append(("RESOLVE REPORT MALFUNCTION", event))
            return e