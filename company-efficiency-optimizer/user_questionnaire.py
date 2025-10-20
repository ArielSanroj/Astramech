"""
User Questionnaire System for Company Efficiency Optimizer
Captures essential company information before file processing
"""

import json
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import typer
from rich.console import Console
from rich.prompt import Prompt, Confirm, IntPrompt
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint

console = Console()

class Industry(Enum):
    """Predefined industry options"""
    MANUFACTURING = "manufacturing"
    SERVICES = "services"
    RETAIL = "retail"
    HEALTHCARE = "healthcare"
    TECHNOLOGY = "technology"
    FINANCE = "finance"
    CONSTRUCTION = "construction"
    AGRICULTURE = "agriculture"
    EDUCATION = "education"
    HOSPITALITY = "hospitality"
    OTHER = "other"

@dataclass
class CompanyProfile:
    """Company profile data structure"""
    company_name: str
    industry: Industry
    employee_count: int
    company_age_years: int
    file_format: str  # "excel" or "pdf"
    is_annual_financial_data: bool
    additional_notes: Optional[str] = None

class UserQuestionnaire:
    """Interactive questionnaire system"""
    
    def __init__(self):
        self.console = Console()
    
    def display_welcome(self) -> None:
        """Display welcome message and instructions"""
        welcome_text = """
🏢 [bold blue]Company Efficiency Optimizer[/bold blue] 🏢

¡Bienvenido! Para brindarte el análisis más preciso y relevante, 
necesitamos conocer algunos detalles sobre tu empresa.

Este cuestionario nos ayudará a:
• Seleccionar los benchmarks correctos para tu industria
• Calcular KPIs más precisos
• Proporcionar recomendaciones específicas
• Validar que el archivo contenga la información correcta

[bold green]¡Comencemos![/bold green]
        """
        
        panel = Panel(
            welcome_text,
            title="[bold blue]Bienvenida[/bold blue]",
            border_style="blue",
            padding=(1, 2)
        )
        self.console.print(panel)
    
    def get_company_name(self) -> str:
        """Get company name"""
        company_name = Prompt.ask(
            "\n[bold cyan]1. ¿Cuál es el nombre de tu empresa?[/bold cyan]",
            default="Mi Empresa"
        )
        return company_name.strip()
    
    def get_industry(self) -> Industry:
        """Get industry selection"""
        self.console.print("\n[bold cyan]2. ¿En qué industria trabaja tu empresa?[/bold cyan]")
        
        # Create industry selection table
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("Opción", style="cyan", width=3)
        table.add_column("Industria", style="white", width=20)
        table.add_column("Descripción", style="dim", width=40)
        
        industries = [
            (1, "Manufactura", "Producción de bienes físicos"),
            (2, "Servicios", "Consultoría, servicios profesionales"),
            (3, "Retail", "Venta al por menor"),
            (4, "Salud", "Servicios médicos y de salud"),
            (5, "Tecnología", "Software, IT, telecomunicaciones"),
            (6, "Finanzas", "Bancos, seguros, inversiones"),
            (7, "Construcción", "Construcción y desarrollo"),
            (8, "Agricultura", "Agricultura y ganadería"),
            (9, "Educación", "Instituciones educativas"),
            (10, "Hospitalidad", "Hoteles, restaurantes, turismo"),
            (11, "Otra", "Otra industria no listada")
        ]
        
        for option, industry, description in industries:
            table.add_row(str(option), industry, description)
        
        self.console.print(table)
        
        while True:
            try:
                choice = IntPrompt.ask(
                    "\n[bold]Selecciona el número de tu industria[/bold]",
                    default=2
                )
                
                if 1 <= choice <= 11:
                    industry_map = {
                        1: Industry.MANUFACTURING,
                        2: Industry.SERVICES,
                        3: Industry.RETAIL,
                        4: Industry.HEALTHCARE,
                        5: Industry.TECHNOLOGY,
                        6: Industry.FINANCE,
                        7: Industry.CONSTRUCTION,
                        8: Industry.AGRICULTURE,
                        9: Industry.EDUCATION,
                        10: Industry.HOSPITALITY,
                        11: Industry.OTHER
                    }
                    return industry_map[choice]
                else:
                    self.console.print("[red]Por favor selecciona un número entre 1 y 11[/red]")
            except ValueError:
                self.console.print("[red]Por favor ingresa un número válido[/red]")
    
    def get_employee_count(self) -> int:
        """Get employee count"""
        while True:
            try:
                employee_count = IntPrompt.ask(
                    "\n[bold cyan]3. ¿Cuántos empleados tiene tu empresa?[/bold cyan]",
                    default=50
                )
                if employee_count > 0:
                    return employee_count
                else:
                    self.console.print("[red]El número de empleados debe ser mayor a 0[/red]")
            except ValueError:
                self.console.print("[red]Por favor ingresa un número válido[/red]")
    
    def get_company_age(self) -> int:
        """Get company age in years"""
        while True:
            try:
                company_age = IntPrompt.ask(
                    "\n[bold cyan]4. ¿Cuántos años tiene tu empresa?[/bold cyan]",
                    default=5
                )
                if company_age >= 0:
                    return company_age
                else:
                    self.console.print("[red]La edad de la empresa no puede ser negativa[/red]")
            except ValueError:
                self.console.print("[red]Por favor ingresa un número válido[/red]")
    
    def get_file_format(self) -> str:
        """Get file format preference"""
        self.console.print("\n[bold cyan]5. ¿Qué tipo de archivo vas a subir?[/bold cyan]")
        
        format_choice = Prompt.ask(
            "Selecciona el formato",
            choices=["excel", "pdf"],
            default="excel"
        )
        
        return format_choice.lower()
    
    def confirm_annual_data(self) -> bool:
        """Confirm that the file contains annual financial data"""
        self.console.print("\n[bold yellow]⚠️  IMPORTANTE: Información Financiera Anual[/bold yellow]")
        
        annual_data_text = """
Para un análisis preciso, necesitamos que el archivo contenga:
• Estados financieros anuales completos
• Estado de Resultados (P&L) del año completo
• Balance General del año completo
• Información de 12 meses de operación

¿El archivo que vas a subir contiene información financiera ANUAL completa?
        """
        
        panel = Panel(
            annual_data_text,
            title="[bold yellow]Verificación de Datos[/bold yellow]",
            border_style="yellow",
            padding=(1, 2)
        )
        self.console.print(panel)
        
        return Confirm.ask(
            "[bold]¿Confirmas que el archivo contiene datos financieros anuales completos?[/bold]",
            default=True
        )
    
    def get_additional_notes(self) -> Optional[str]:
        """Get additional notes (optional)"""
        notes = Prompt.ask(
            "\n[bold cyan]6. Notas adicionales (opcional)[/bold cyan]",
            default=""
        )
        return notes.strip() if notes.strip() else None
    
    def display_summary(self, profile: CompanyProfile) -> None:
        """Display questionnaire summary"""
        summary_text = f"""
[bold]Resumen del Perfil de la Empresa:[/bold]

🏢 [bold]Empresa:[/bold] {profile.company_name}
🏭 [bold]Industria:[/bold] {profile.industry.value.title()}
👥 [bold]Empleados:[/bold] {profile.employee_count:,}
📅 [bold]Antigüedad:[/bold] {profile.company_age_years} años
📄 [bold]Formato de archivo:[/bold] {profile.file_format.upper()}
📊 [bold]Datos anuales:[/bold] {'Sí' if profile.is_annual_financial_data else 'No'}
        """
        
        if profile.additional_notes:
            summary_text += f"\n📝 [bold]Notas:[/bold] {profile.additional_notes}"
        
        panel = Panel(
            summary_text,
            title="[bold green]Perfil de la Empresa[/bold green]",
            border_style="green",
            padding=(1, 2)
        )
        self.console.print(panel)
    
    def run_questionnaire(self) -> CompanyProfile:
        """Run the complete questionnaire"""
        self.display_welcome()
        
        company_name = self.get_company_name()
        industry = self.get_industry()
        employee_count = self.get_employee_count()
        company_age = self.get_company_age()
        file_format = self.get_file_format()
        is_annual_data = self.confirm_annual_data()
        additional_notes = self.get_additional_notes()
        
        profile = CompanyProfile(
            company_name=company_name,
            industry=industry,
            employee_count=employee_count,
            company_age_years=company_age,
            file_format=file_format,
            is_annual_financial_data=is_annual_data,
            additional_notes=additional_notes
        )
        
        self.display_summary(profile)
        
        # Confirm before proceeding
        if not Confirm.ask("\n[bold]¿Proceder con el análisis con esta información?[/bold]", default=True):
            self.console.print("[yellow]Cuestionario cancelado. Puedes ejecutarlo nuevamente.[/yellow]")
            raise typer.Exit(1)
        
        return profile
    
    def save_profile(self, profile: CompanyProfile, filename: str = "company_profile.json") -> None:
        """Save company profile to JSON file"""
        profile_data = {
            "company_name": profile.company_name,
            "industry": profile.industry.value,
            "employee_count": profile.employee_count,
            "company_age_years": profile.company_age_years,
            "file_format": profile.file_format,
            "is_annual_financial_data": profile.is_annual_financial_data,
            "additional_notes": profile.additional_notes
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(profile_data, f, indent=2, ensure_ascii=False)
        
        self.console.print(f"\n[green]✅ Perfil guardado en: {filename}[/green]")
    
    def load_profile(self, filename: str = "company_profile.json") -> Optional[CompanyProfile]:
        """Load company profile from JSON file"""
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return CompanyProfile(
                company_name=data["company_name"],
                industry=Industry(data["industry"]),
                employee_count=data["employee_count"],
                company_age_years=data["company_age_years"],
                file_format=data["file_format"],
                is_annual_financial_data=data["is_annual_financial_data"],
                additional_notes=data.get("additional_notes")
            )
        except (FileNotFoundError, KeyError, ValueError) as e:
            self.console.print(f"[yellow]No se pudo cargar el perfil: {e}[/yellow]")
            return None

def main():
    """Main function for testing the questionnaire"""
    questionnaire = UserQuestionnaire()
    
    try:
        profile = questionnaire.run_questionnaire()
        questionnaire.save_profile(profile)
        
        console.print("\n[bold green]🎉 ¡Cuestionario completado exitosamente![/bold green]")
        console.print("Ahora puedes proceder con el análisis de tu archivo financiero.")
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Cuestionario interrumpido por el usuario.[/yellow]")
    except typer.Exit:
        pass

if __name__ == "__main__":
    typer.run(main)