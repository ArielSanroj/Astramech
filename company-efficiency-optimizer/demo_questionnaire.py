"""
Demo del Sistema de Cuestionario
Muestra cómo funciona el cuestionario interactivo
"""

import typer
from rich.console import Console
from user_questionnaire import UserQuestionnaire

console = Console()

def main():
    """Demo del cuestionario interactivo"""
    
    console.print("[bold blue]🎯 Demo del Sistema de Cuestionario[/bold blue]")
    console.print("Este demo te mostrará cómo funciona el cuestionario interactivo\n")
    
    questionnaire = UserQuestionnaire()
    
    try:
        # Ejecutar el cuestionario
        profile = questionnaire.run_questionnaire()
        
        # Mostrar información adicional
        console.print("\n" + "="*60)
        console.print("[bold green]🎉 ¡Cuestionario Completado![/bold green]")
        console.print("="*60)
        
        console.print(f"\n[bold]Información capturada:[/bold]")
        console.print(f"• Empresa: {profile.company_name}")
        console.print(f"• Industria: {profile.industry.value}")
        console.print(f"• Empleados: {profile.employee_count:,}")
        console.print(f"• Antigüedad: {profile.company_age_years} años")
        console.print(f"• Formato: {profile.file_format.upper()}")
        console.print(f"• Datos anuales: {'Sí' if profile.is_annual_financial_data else 'No'}")
        
        if profile.additional_notes:
            console.print(f"• Notas: {profile.additional_notes}")
        
        # Guardar perfil
        questionnaire.save_profile(profile, "demo_profile.json")
        
        console.print(f"\n[bold green]✅ Perfil guardado en: demo_profile.json[/bold green]")
        console.print("\n[bold]Próximos pasos:[/bold]")
        console.print("1. Usa este perfil con el procesador de archivos")
        console.print("2. Ejecuta: python enhanced_universal_processor.py tu_archivo.xlsx")
        console.print("3. El sistema usará automáticamente este perfil para un análisis más preciso")
        
    except KeyboardInterrupt:
        console.print("\n[yellow]Demo interrumpido por el usuario.[/yellow]")
    except Exception as e:
        console.print(f"[red]Error en el demo: {e}[/red]")

if __name__ == "__main__":
    typer.run(main)