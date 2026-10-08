"""Interfaz interna del encargado para atención B2C presencial; consume AppService."""
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime, timedelta
import csv
from src.domain.exceptions import MediCoreError, ValidacionError
from src.ui.widgets import BG, INK, MUTED, TEAL, ASSETS, label, button, table, ScrollFrame, configure_style


class MediCoreApp(tk.Tk):
    def __init__(self, servicio):
        super().__init__()
        self.servicio = servicio
        self.title('MediCore | Gestión del centro médico')
        self.geometry('1280x820'); self.minsize(960,650); self.configure(bg=BG)
        configure_style(self)
        self.images = {p.stem: tk.PhotoImage(file=str(p)) for p in ASSETS.glob('*.png')}
        if 'logo' in self.images: self.iconphoto(True, self.images['logo'])
        pacientes = servicio.listar_pacientes()
        self.patient_id = pacientes[0].id if pacientes else None
        self.page = 'Resumen'; self.navbuttons = {}
        self._layout(); self.navigate('Resumen')

    def report_callback_exception(self, exc_type, exc, tb):
        if isinstance(exc, MediCoreError):
            messagebox.showwarning('Revisa los datos', str(exc), parent=self)
        else:
            import traceback
            traceback.print_exception(exc_type, exc, tb)
            messagebox.showerror('No se completó la operación', 'Ocurrió un error inesperado. Revisa la terminal para conocer el detalle.', parent=self)

    def _layout(self):
        header = tk.Frame(self, bg='white', height=82)
        header.pack(fill='x'); header.pack_propagate(False)
        brand = tk.Frame(header, bg='white'); brand.pack(side='left', padx=25)
        label(brand, '', bg='white', image=self.images.get('logo')).pack(side='left', padx=(0,10))
        label(brand,'MediCore',22,True).pack(side='left')
        label(header,'CUSCO  /  ATENCIÓN PRESENCIAL',9,color=MUTED).pack(side='left',padx=28)
        label(header,'RECEPCIÓN  ·  ENCARGADO',10,True,color=TEAL).pack(side='right',padx=25)
        foot = tk.Frame(self,bg='#E5EDF2'); foot.pack(side='bottom',fill='x')
        label(foot,'  DEMO ACADÉMICA LOCAL  ·  Datos ficticios  ·  Sin autenticación ni pagos en línea',9,color=MUTED).pack(side='left',padx=12,pady=7)
        body = tk.Frame(self,bg=BG); body.pack(fill='both',expand=True)
        self.sidebar = tk.Frame(body,bg='#173449',width=215); self.sidebar.pack(side='left',fill='y'); self.sidebar.pack_propagate(False)
        self.content = tk.Frame(body,bg=BG); self.content.pack(side='left',fill='both',expand=True,padx=25,pady=20)
        self._navigation()

    def _navigation(self):
        for w in self.sidebar.winfo_children(): w.destroy()
        self.navbuttons = {}
        label(self.sidebar,'CENTRO MÉDICO',9,True,color='#8BA9B9').pack(anchor='w',padx=22,pady=(26,16))
        pages = [('Resumen','home'),('Agenda','calendar'),('Pacientes','patients'),('Médicos','doctors'),('Historias clínicas','history')]
        for name, icon in pages:
            b = tk.Button(self.sidebar,text='  '+name,image=self.images.get(icon),compound='left',anchor='w',
                          command=lambda n=name:self.navigate(n), bg='#173449',fg='white',bd=0,padx=20,pady=15,
                          font=('Segoe UI',10,'bold'),activebackground='#285467',activeforeground='white',cursor='hand2')
            b.pack(fill='x',padx=10,pady=3); self.navbuttons[name] = b
        label(self.sidebar,'Atención organizada.\nPacientes primero.',16,True,color='white',justify='left').pack(side='bottom',anchor='w',padx=22,pady=28)

    def navigate(self, name):
        self.page = name
        for key,b in self.navbuttons.items(): b.configure(bg='#285467' if key==name else '#173449')
        for w in self.content.winfo_children(): w.destroy()
        {'Resumen':self.dashboard,'Agenda':self.appointments,'Pacientes':self.patients,
         'Médicos':self.doctors,'Historias clínicas':self.history}[name]()

    def heading(self, title, subtitle):
        label(self.content,title,24,True).pack(anchor='w')
        label(self.content,subtitle,10,color=MUTED).pack(anchor='w',pady=(5,16))

    def patient_selector(self):
        row = tk.Frame(self.content,bg=BG); row.pack(fill='x',pady=(0,12))
        label(row,'Paciente seleccionado:',10,color=MUTED).pack(side='left',padx=(0,10))
        patients = self.servicio.listar_pacientes()
        lookup = {p.descripcion():p.id for p in patients}
        current = next((k for k,v in lookup.items() if v==self.patient_id),'')
        value = tk.StringVar(value=current)
        combo = ttk.Combobox(row,textvariable=value,values=list(lookup),state='readonly',width=35)
        combo.pack(side='left')
        def change(event):
            self.patient_id=lookup[value.get()]; self.navigate(self.page)
        combo.bind('<<ComboboxSelected>>',change)
        button(row,'+ Registrar paciente',self.new_patient,True).pack(side='right')
        return self.patient_id is not None

    def stats(self, parent, patient_id=None):
        data = self.servicio.indicadores(patient_id)
        row = tk.Frame(parent,bg=BG); row.pack(fill='x',pady=(6,18))
        for i,(state,title,color) in enumerate([('PROGRAMADA','Citas programadas','#946000'),('ATENDIDA','Atenciones registradas',TEAL),('CANCELADA','Citas canceladas','#A33E4F')]):
            box = tk.Frame(row,bg='white',padx=20,pady=15)
            box.grid(row=0,column=i,sticky='ew',padx=(0,12 if i<2 else 0)); row.columnconfigure(i,weight=1)
            label(box,str(data[state]),27,True,color=color).pack(anchor='w')
            label(box,title,10,color=MUTED).pack(anchor='w',pady=(3,0))

    def doctors(self):
        self.heading('Médicos y disponibilidad','Selecciona al paciente y al profesional para programar una cita desde recepción.')
        self.patient_selector()
        controls=tk.Frame(self.content,bg=BG);controls.pack(fill='x')
        q=tk.StringVar();special=tk.StringVar(value='Todas las especialidades')
        entry=ttk.Entry(controls,textvariable=q,width=25);entry.pack(side='left',padx=(0,8))
        combo=ttk.Combobox(controls,textvariable=special,values=['Todas las especialidades']+self.servicio.especialidades(),state='readonly',width=24);combo.pack(side='left')
        button(controls,'+ Nuevo médico',self.new_doctor).pack(side='right')
        scroll=ScrollFrame(self.content);scroll.pack(fill='both',expand=True,pady=(15,0))
        def render(*_):
            for w in scroll.body.winfo_children():w.destroy()
            doctors=[m for m in self.servicio.listar_medicos() if q.get().casefold() in (m.nombre+' '+m.especialidad).casefold() and (special.get()=='Todas las especialidades' or m.especialidad==special.get())]
            for m in doctors:
                card=tk.Frame(scroll.body,bg='white',padx=18,pady=18);card.pack(fill='x',pady=(0,12))
                label(card,'',image=self.images.get('doctor'),bg='white').pack(side='left',padx=(0,18))
                text=tk.Frame(card,bg='white');text.pack(side='left',fill='x',expand=True)
                label(text,m.especialidad.upper(),9,True,color=TEAL).pack(anchor='w')
                label(text,m.nombre,17,True).pack(anchor='w',pady=4)
                label(text,f'CMP {m.cmp}  ·  Consulta de 30 minutos',10,color=MUTED).pack(anchor='w')
                label(text,m.detalle,10,color=MUTED,wraplength=340,justify='left').pack(anchor='w',pady=(6,0))
                right=tk.Frame(card,bg='white');right.pack(side='right',padx=(12,0))
                label(right,f'S/ {m.tarifa:.2f}',20,True).pack(anchor='e')
                label(right,'Pago presencial',9,color=MUTED).pack(anchor='e',pady=(0,10))
                button(right,'Programar cita',lambda mid=m.id:self.booking(mid)).pack(anchor='e')
            if not doctors:label(scroll.body,'No encontramos médicos con esos filtros.',12,color=MUTED).pack(pady=35)
        q.trace_add('write',render);combo.bind('<<ComboboxSelected>>',render);render()

    def dialog(self,title,size='560x570'):
        win=tk.Toplevel(self);win.title(title);win.geometry(size);win.configure(bg='white');win.transient(self);win.grab_set()
        win.minsize(480,400)
        body=tk.Frame(win,bg='white',padx=24,pady=20);body.pack(fill='both',expand=True)
        label(body,title,19,True).pack(anchor='w',pady=(0,16))
        return win,body

    def field(self,body,title,value=''):
        label(body,title,10,True).pack(anchor='w',pady=(8,4))
        var=tk.StringVar(value=value);ttk.Entry(body,textvariable=var).pack(fill='x')
        return var

    def new_patient(self):
        win,body=self.dialog('Registrar paciente')
        label(body,'Usa datos ficticios para esta demostración.',10,color=MUTED).pack(anchor='w')
        name=self.field(body,'Nombre completo *');dni=self.field(body,'DNI · 8 dígitos *')
        phone=self.field(body,'Celular · opcional');email=self.field(body,'Correo · opcional')
        def save():
            p=self.servicio.registrar_paciente(name.get(),dni.get(),phone.get(),email.get())
            self.patient_id=p.id;win.destroy();self.navigate(self.page)
            messagebox.showinfo('Paciente registrado','El paciente se registró correctamente.',parent=self)
        button(body,'Guardar paciente',save).pack(fill='x',pady=24)

    def new_doctor(self):
        win,body=self.dialog('Registrar médico','560x640')
        name=self.field(body,'Nombre completo *');special=self.field(body,'Especialidad *');cmp=self.field(body,'CMP único *')
        cost=self.field(body,'Tarifa en soles *');desc=self.field(body,'Presentación breve','Atención presencial en Cusco.')
        def save():
            self.servicio.registrar_medico(name.get(),special.get(),cmp.get(),cost.get(),desc.get())
            win.destroy();self.navigate(self.page)
        button(body,'Guardar médico',save).pack(fill='x',pady=22)

    def booking(self, medico_id):
        if not self.patient_id:
            messagebox.showinfo('Selecciona un paciente','Primero registra o selecciona un paciente.',parent=self);self.new_patient();return
        m=self.servicio.medico(medico_id)
        win,body=self.dialog('Programar cita','580x690')
        label(body,f'{m.nombre} · {m.especialidad}',12,True).pack(anchor='w')
        label(body,'Paciente *',10,True).pack(anchor='w',pady=(10,4))
        patients={p.descripcion():p.id for p in self.servicio.listar_pacientes()}
        patient_var=tk.StringVar(value=next(k for k,v in patients.items() if v==self.patient_id))
        patient_combo=ttk.Combobox(body,textvariable=patient_var,values=list(patients),state='readonly')
        patient_combo.pack(fill='x',pady=(0,8))
        label(body,f'S/ {m.tarifa:.2f} · 30 minutos · Pago presencial',11,color=TEAL).pack(anchor='w')
        tomorrow=self.servicio.ahora().date()+timedelta(days=1)
        if tomorrow.weekday()==6:tomorrow+=timedelta(days=1)
        fecha=self.field(body,'Fecha (AAAA-MM-DD)',tomorrow.isoformat())
        label(body,'Horario disponible',10,True).pack(anchor='w',pady=(12,4))
        hora=tk.StringVar();times=ttk.Combobox(body,textvariable=hora,state='readonly');times.pack(fill='x')
        hint=label(body,'',10,color=MUTED);hint.pack(anchor='w',pady=6)
        def refresh():
            slots=self.servicio.horarios_disponibles(medico_id,fecha.get(),patients[patient_var.get()])
            values=[s.strftime('%H:%M') for s in slots];times.configure(values=values);hora.set(values[0] if values else '')
            hint.configure(text=f'{len(values)} turnos disponibles' if values else 'No hay turnos. Prueba otra fecha.')
        button(body,'Actualizar horarios',refresh,True).pack(anchor='w',pady=6)
        motivo=self.field(body,'Motivo de consulta *')
        label(body,'Presencial en Cusco · Reserva de demostración.\nNo se solicita tarjeta ni se realiza ningún cobro.',10,color=MUTED,justify='left').pack(anchor='w',pady=15)
        def save():
            if not hora.get():raise ValidacionError('Selecciona un horario disponible.')
            try:inicio=datetime.fromisoformat(fecha.get()+'T'+hora.get())
            except ValueError:raise ValidacionError('La fecha o la hora no son válidas.') from None
            self.patient_id=patients[patient_var.get()]
            c=self.servicio.programar_cita(self.patient_id,medico_id,inicio,motivo.get())
            win.destroy();self.navigate('Agenda')
            messagebox.showinfo('Reserva confirmada',f'Código: {c.id}\n{inicio:%d/%m/%Y a las %H:%M}\n{m.nombre}\nS/ {c.tarifa:.2f} · Pago presencial',parent=self)
        button(body,'Guardar cita',save).pack(fill='x',pady=8)
        patient_combo.bind('<<ComboboxSelected>>',lambda event:refresh())
        refresh()

    def appointments(self):
        self.heading('Agenda del centro médico','Programa citas y selecciona una fila para consultar, cancelar o registrar una atención.')
        filters=tk.Frame(self.content,bg=BG);filters.pack(fill='x')
        state=tk.StringVar(value='TODAS');date=tk.StringVar()
        ttk.Combobox(filters,textvariable=state,values=['TODAS','PROGRAMADA','ATENDIDA','CANCELADA'],state='readonly',width=16).pack(side='left')
        label(filters,'Fecha:',10).pack(side='left',padx=(12,5));ttk.Entry(filters,textvariable=date,width=13).pack(side='left')
        label(filters,'AAAA-MM-DD',9,color=MUTED).pack(side='left',padx=5)
        columns=[('date','Fecha / hora',155),('patient','Paciente',170),('doctor','Médico',165),('special','Especialidad',145),('status','Estado',120),('price','Tarifa',85)]
        actions=tk.Frame(self.content,bg=BG);actions.pack(side='bottom',fill='x',pady=(14,0))
        self.tree=table(self.content,columns)
        def render():
            if date.get():
                try:datetime.strptime(date.get(),'%Y-%m-%d')
                except ValueError:raise ValidacionError('Usa una fecha válida con formato AAAA-MM-DD.') from None
            for item in self.tree.get_children():self.tree.delete(item)
            rows=self.servicio.listar_citas(None,None if state.get()=='TODAS' else state.get(),date.get() or None)
            for c in rows:
                p=self.servicio.paciente(c.paciente_id);m=self.servicio.medico(c.medico_id)
                self.tree.insert('', 'end',iid=c.id,values=(c.inicio.strftime('%d/%m/%Y %H:%M'),p.nombre,m.nombre,m.especialidad,c.estado,f'S/ {c.tarifa:.2f}'),tags=(c.estado,))
            count.configure(text=f'{len(rows)} citas encontradas')
        button(filters,'Filtrar',render,True).pack(side='left',padx=8)
        count=label(actions,'',9,color=MUTED);count.pack(side='right')
        button(actions,'Ver detalle',self.cita_detail,True).pack(side='left',padx=(0,8))
        button(actions,'Cancelar cita',self.cancel,True).pack(side='left',padx=(0,8))
        button(actions,'Registrar atención',self.attend).pack(side='left')
        button(filters,'+ Nueva cita',lambda:self.navigate('Médicos')).pack(side='right')
        self.tree.bind('<Double-1>',lambda e:self.cita_detail());render()

    def selected(self):
        items=self.tree.selection()
        if not items:raise ValidacionError('Selecciona una cita de la tabla.')
        return self.servicio.cita(items[0])

    def cita_detail(self):
        c=self.selected();m=self.servicio.medico(c.medico_id);p=self.servicio.paciente(c.paciente_id)
        win,body=self.dialog('Detalle de cita','560x480')
        text=f'Código: {c.id}\n\nPaciente: {p.nombre}\nMédico: {m.nombre}\nEspecialidad: {m.especialidad}\nFecha: {c.inicio:%d/%m/%Y %H:%M}\nEstado: {c.estado}\nTarifa: S/ {c.tarifa:.2f}\n\nMotivo: {c.motivo}'
        area=tk.Text(body,font=('Segoe UI',11),bg='white',fg=INK,bd=0,wrap='word');area.pack(fill='both',expand=True);area.insert('1.0',text);area.configure(state='disabled')
        button(body,'Cerrar',win.destroy,True).pack(anchor='e',pady=10)

    def cancel(self):
        c=self.selected()
        if c.estado!='PROGRAMADA':raise ValidacionError('Solo puedes cancelar citas programadas.')
        if messagebox.askyesno('Cancelar cita','¿Deseas cancelar esta cita? El turno quedará disponible.',parent=self):
            self.servicio.cancelar_cita(c.id);self.navigate(self.page)

    def attend(self):
        c=self.selected()
        if c.estado!='PROGRAMADA':raise ValidacionError('Selecciona una cita programada.')
        if c.inicio>self.servicio.ahora():raise ValidacionError('La cita aún no ha comenzado.')
        win,body=self.dialog('Registrar atención','600x600')
        label(body,self.servicio.paciente(c.paciente_id).nombre,13,True).pack(anchor='w')
        label(body,'Diagnóstico indicado por el profesional *',10,True).pack(anchor='w',pady=(15,5))
        diagnosis=tk.Text(body,height=5,font=('Segoe UI',11),wrap='word',bg=BG,relief='flat');diagnosis.pack(fill='both',expand=True)
        label(body,'Indicaciones del profesional / seguimiento *',10,True).pack(anchor='w',pady=(15,5))
        indications=tk.Text(body,height=5,font=('Segoe UI',11),wrap='word',bg=BG,relief='flat');indications.pack(fill='both',expand=True)
        def save():
            self.servicio.registrar_atencion(c.id,diagnosis.get('1.0','end').strip(),indications.get('1.0','end').strip())
            win.destroy();self.navigate(self.page)
            messagebox.showinfo('Atención guardada','La cita ahora está ATENDIDA y aparece en la historia del paciente.',parent=self)
        button(body,'Guardar atención',save).pack(fill='x',pady=(18,0))

    def history(self):
        self.heading('Historias clínicas','Selecciona al paciente para consultar los registros de atención del centro médico.')
        if not self.patient_selector():return
        scroll=ScrollFrame(self.content);scroll.pack(fill='both',expand=True)
        records=self.servicio.obtener_historia(self.patient_id)
        for r in records:
            c=self.servicio.cita(r.cita_id);m=self.servicio.medico(c.medico_id)
            card=tk.Frame(scroll.body,bg='white',padx=22,pady=20);card.pack(fill='x',pady=(0,12))
            label(card,f'{c.inicio:%d/%m/%Y} · {m.especialidad}',11,True,color=TEAL).pack(anchor='w')
            label(card,m.nombre,16,True).pack(anchor='w',pady=6)
            label(card,'Diagnóstico',10,True).pack(anchor='w',pady=(10,3))
            d=label(card,r.diagnostico,11,justify='left',anchor='w');d.pack(fill='x')
            label(card,'Indicaciones',10,True).pack(anchor='w',pady=(12,3))
            i=label(card,r.indicaciones,11,color=MUTED,justify='left',anchor='w');i.pack(fill='x')
            card.bind('<Configure>',lambda e,ls=(d,i):[x.configure(wraplength=max(200,e.width-50)) for x in ls])
        if not records:label(scroll.body,'El paciente no tiene atenciones registradas.\nLos registros aparecerán aquí al guardar una atención desde Agenda.',12,color=MUTED,justify='center').pack(pady=65)

    def patients(self):
        self.heading('Pacientes','Registro central de pacientes. Selecciona una fila para programar una cita o consultar su historia.')
        controls=tk.Frame(self.content,bg=BG);controls.pack(fill='x')
        q=tk.StringVar();ttk.Entry(controls,textvariable=q,width=40).pack(side='left')
        label(controls,'Buscar por nombre o DNI',10,color=MUTED).pack(side='left',padx=12)
        button(controls,'+ Nuevo paciente',self.new_patient).pack(side='right')
        actions=tk.Frame(self.content,bg=BG);actions.pack(side='bottom',fill='x',pady=(14,0))
        def open_patient(destination):
            selected=tree.selection()
            if not selected:raise ValidacionError('Selecciona un paciente de la tabla.')
            self.patient_id=selected[0];self.navigate(destination)
        button(actions,'Programar cita',lambda:open_patient('Médicos')).pack(side='left',padx=(0,10))
        button(actions,'Consultar historia',lambda:open_patient('Historias clínicas'),True).pack(side='left')
        tree=table(self.content,[('name','Nombre',220),('dni','DNI',105),('phone','Celular',125),('email','Correo',220)])
        def render(*_):
            for item in tree.get_children():tree.delete(item)
            for p in self.servicio.listar_pacientes():
                if q.get().casefold() in (p.nombre+' '+p.dni).casefold():tree.insert('','end',iid=p.id,values=(p.nombre,p.dni,p.telefono,p.correo))
        q.trace_add('write',render);render()

    def dashboard(self):
        self.heading('Panel del encargado','Pacientes, citas y atenciones del centro médico en un solo lugar.')
        self.stats(self.content)
        panel=tk.Frame(self.content,bg='white',padx=22,pady=22);panel.pack(fill='x',pady=5)
        label(panel,'Control de atención del centro médico',18,True).pack(anchor='w')
        label(panel,'',image=self.images.get('care'),bg='white').pack(side='right',padx=(20,0))
        label(panel,f'{len(self.servicio.pacientes)} pacientes  ·  {len(self.servicio.medicos)} médicos  ·  {len(self.servicio.especialidades())} especialidades',12,color=MUTED).pack(anchor='w',pady=14)
        total=sum(c.tarifa for c in self.servicio.citas.values() if c.estado=='ATENDIDA')
        label(panel,f'Valor de atenciones registradas: S/ {total:.2f}',14,True,color=TEAL).pack(anchor='w')
        label(panel,'Este importe no acredita pagos recibidos.',10,color=MUTED).pack(anchor='w',pady=(5,15))
        button(panel,'Abrir agenda',lambda:self.navigate('Agenda')).pack(anchor='w')
        box=tk.Frame(self.content,bg='#DDF1EF',padx=22,pady=20);box.pack(fill='x',pady=18)
        label(box,'Cómo registrar una atención',14,True).pack(anchor='w')
        label(box,'Selecciona una cita programada que ya haya comenzado, pulsa\n“Registrar atención” y guarda el diagnóstico y las indicaciones.',11,justify='left').pack(anchor='w',pady=10)
        label(box,'El encargado registra el diagnóstico y las indicaciones proporcionados por el profesional.',10,color=TEAL).pack(anchor='w')
        button(self.content,'Exportar agenda a CSV',self.export_csv,True).pack(anchor='w')

    def export_csv(self):
        path=filedialog.asksaveasfilename(parent=self,title='Exportar agenda',defaultextension='.csv',initialfile='agenda_medicore.csv',filetypes=[('CSV','*.csv')])
        if not path:return
        try:
            with open(path,'w',encoding='utf-8-sig',newline='') as f:
                writer=csv.writer(f);writer.writerow(['Código','Fecha','Paciente','Médico','Especialidad','Estado','Tarifa'])
                def safe(text):
                    text=str(text)
                    return "'"+text if text.startswith(('=','+','-','@','\t','\r')) else text
                for c in self.servicio.listar_citas():
                    p=self.servicio.paciente(c.paciente_id);m=self.servicio.medico(c.medico_id)
                    writer.writerow([safe(v) for v in [c.id,c.inicio.isoformat(),p.nombre,m.nombre,m.especialidad,c.estado,f'{c.tarifa:.2f}']])
        except OSError as exc:raise ValidacionError(f'No se pudo exportar: {exc}') from exc
        messagebox.showinfo('Exportación lista','La agenda se guardó en el archivo elegido.',parent=self)


def iniciar(servicio):
    app=MediCoreApp(servicio)
    app.mainloop()


def iniciar_cli(servicio):
    print('MediCore · Resumen de registros locales')
    print(f'Pacientes: {len(servicio.pacientes)} | Médicos: {len(servicio.medicos)}')
    for estado,total in servicio.indicadores().items():print(f'{estado}: {total}')
    for c in servicio.listar_citas():print(c.inicio,servicio.paciente(c.paciente_id).nombre,c.estado)
