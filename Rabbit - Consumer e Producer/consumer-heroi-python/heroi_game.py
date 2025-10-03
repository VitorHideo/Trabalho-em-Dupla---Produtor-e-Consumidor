"""Consumidor de heróis -> partida auto 3x3 (roles, ultimates, MVP)."""
import os,json,time,random,threading,traceback
try:
    from dotenv import load_dotenv;load_dotenv()
except: pass
import pika
class Hz:
    def __init__(self,d):
        def g(k): return d.get(k)
        def num(k):
            try: return float(g(k) or 0)
            except: return 0.0
        self.nome=str(g('nome') or 'Desconhecido'); self.funcao=str(g('funcao') or g('categoria') or 'Other')
        self.vb=num('vidaBase'); self.va=num('vidaArmadura'); self.ve=num('vidaEscudo')
        self.dp=num('danoPrincipal'); self.ds=num('danoSecundario'); self.cb=num('curaBase')
        self.frase=str(g('fraseUlt') or '')
        try: self.idade=int(g('idade') or 0)
        except: self.idade=0
        self.raw=dict(d)
        if (self.vb+self.va+self.ve)<=0: self.vb=120.0
        if self.dp<=0 and self.ds<=0: self.dp=18.0
        self.hp=self.dano=self.cura=self.k=self.acts=self.ults=0; self.reset()
    def reset(self): self.hp=max(0.0,self.vb+self.va+self.ve); self.dano=self.cura=self.k=self.acts=self.ults=0
    def role(self): return (self.funcao or 'Other').title()
    def base_dmg(self):
        dmg=self.dp or self.ds or 10
        if self.role()=='Sniper': dmg*=1.3
        return max(1,dmg)
    def heal_amt(self): return self.cb or 15
    def leva(self,q):
        if self.role()=='Tank': q*=0.8
        self.hp-=q; return q


# Estado global
h_all={}; h_ord=[]; in_match=False; stop_evt=threading.Event(); lock=threading.Lock()


def cria_heroi(d): return Hz(d)


def consumidor(cfg):
    while not stop_evt.is_set():
        try:
            cred = pika.PlainCredentials(cfg['user'], cfg['password'])
            params = pika.ConnectionParameters(
                host=cfg['host'], port=cfg['port'], virtual_host=cfg['vhost'],
                credentials=cred, heartbeat=30, blocked_connection_timeout=60
            )
            conn = pika.BlockingConnection(params)
            ch = conn.channel()
            ch.queue_declare(queue=cfg['queue'], passive=False, durable=False)
            if cfg['exchange']:
                ch.exchange_declare(exchange=cfg['exchange'], exchange_type=cfg['exchange_type'], durable=True)
                ch.queue_bind(queue=cfg['queue'], exchange=cfg['exchange'], routing_key=cfg['routing_key'])
            ch.basic_qos(prefetch_count=cfg['prefetch'])

            def cb(_c, m, p, body):  # type: ignore
                global in_match
                try:
                    d = json.loads(body.decode('utf-8'))
                    hz = cria_heroi(d)
                    novo = False
                    with lock:
                        if hz.nome not in h_all:
                            h_ord.append(hz.nome)
                            novo = True
                        h_all[hz.nome] = hz
                        tot = len(h_ord)
                    if novo:
                        print(f"[NOVO] {hz.nome} ({hz.funcao}) total={tot}")
                    else:
                        print(f"[ATUALIZADO] {hz.nome}")
                    if tot >= 6 and not in_match:
                        print("\n===== PARTIDA AUTO 3x3 =====")
                        threading.Thread(target=rola_partida, daemon=True).start()
                except Exception:
                    traceback.print_exc()
                finally:
                    _c.basic_ack(delivery_tag=m.delivery_tag)

            ch.basic_consume(queue=cfg['queue'], on_message_callback=cb)
            ch.start_consuming()
        except Exception as e:
            if not stop_evt.is_set():
                print('[ERRO MQ]', e)
                time.sleep(cfg['reconnect'])


def vivos(team):
    r=[]
    for h in team:
        if h.hp>0: r.append(h)
    return r

def escolher_alvo_hp_baixo(lst):
    alvo=None
    for h in lst:
        if alvo is None or h.hp<alvo.hp: alvo=h
    return alvo

def escolher_aliado_mais_fraco(lst):
    alvo=None; pior=None
    for h in lst:
        mx=h.vb+h.va+h.ve+0.1; ratio=h.hp/mx
        if pior is None or ratio<pior: pior=ratio; alvo=h
    return alvo

def ordenar_por_total(lst):
    a=list(lst); n=len(a)
    for i in range(n):
        m=i
        for j in range(i+1,n):
            if (a[j].dano+a[j].cura)>(a[m].dano+a[m].cura): m=j
        if m!=i: a[i],a[m]=a[m],a[i]
    return a

def rola_partida():
    global in_match
    with lock:
        if in_match:
            return
        in_match = True
        nomes = h_ord[:6]
        # embaralha simples (sem usar shuffle direto para ficar claro)
        todos = list(nomes)
        for i in range(len(todos)):
            j = random.randint(0, len(todos)-1)
            todos[i], todos[j] = todos[j], todos[i]
        a_n = todos[:3]
        b_n = todos[3:6]
        ta = [h_all[n] for n in a_n]
        tb = [h_all[n] for n in b_n]
    for h in ta+tb: h.reset()

    print('Time A:', ', '.join(a_n))
    print('Time B:', ', '.join(b_n))
    print('--------------------------------')

    mults=[0.5,1.0,1.5,2.0]; turn=1; ini=time.time()
    while len(vivos(ta))>0 and len(vivos(tb))>0:
        print(f"\n-- TURNO {turn} --")
        # decide quem ataca primeiro neste turno para diminuir vantagem fixa
        first = random.randint(0,1)  # 0 -> A, 1 -> B
        sequencia=[(ta,tb),(tb,ta)] if first==0 else [(tb,ta),(ta,tb)]
        for par in sequencia:
            atk = par[0]
            dfd = par[1]
            if len(vivos(dfd)) == 0:
                break
            for h in atk:
                if h.hp <= 0 or len(vivos(dfd)) == 0:
                    continue
                m = random.choice(mults)
                h.acts += 1
                r = h.role()
                # ultimate
                uc=0.15
                try: uc=float(h.raw.get('ultChance',uc))
                except: pass
                ult_on=False; boost=1.0
                if h.frase and random.random()<uc:
                    ult_on=True; h.ults+=1; print(f'ULTIMATE! {h.nome}: "{h.frase}"')
                if r in ['Support','Healer']:
                    alvos = vivos(atk)
                    alvo = escolher_aliado_mais_fraco(alvos)
                    heal=h.heal_amt()*m
                    if ult_on:
                        try: boost=float(h.raw.get('ultHealBoost',1.6))
                        except: boost=1.6
                        heal*=boost
                    antes = alvo.hp
                    mx = alvo.vb + alvo.va + alvo.ve
                    alvo.hp = min(mx, alvo.hp + heal)
                    real = alvo.hp - antes
                    h.cura += real
                    tag = f' (ULT x{boost:.2f})' if ult_on else ''
                    print(f'{h.nome} (SUPPORT) cura {alvo.nome} +{real:.0f} (x{m}{tag}) HP={alvo.hp:.0f}')
                else:
                    vivos_def = vivos(dfd)
                    alvo = escolher_alvo_hp_baixo(vivos_def)
                    dmg=h.base_dmg()*m
                    if ult_on:
                        try: boost=float(h.raw.get('ultDamageBoost',1.75))
                        except: boost=1.75
                        dmg*=boost
                    real = alvo.leva(dmg)
                    h.dano += real
                    ext = f' (ULT x{boost:.2f})' if ult_on else ''
                    msg = f'{h.nome} ataca {alvo.nome} {real:.0f} (x{m}{ext})'
                    if alvo.hp<=0:
                        h.k += 1
                        msg += ' -> ELIMINADO'
                    print(msg)
        turn+=1
        if turn>200: print('\n[Limite 200]'); break

    dur=time.time()-ini; a_alive=len(vivos(ta))>0; b_alive=len(vivos(tb))>0
    print('\n===== FIM =====')
    ven=None
    if a_alive and not b_alive: ven='A'
    elif b_alive and not a_alive: ven='B'
    print('VENCEDOR: Time',ven) if ven else print('EMPATE')
    print(f'Turnos: {turn-1}  Duracao: {dur:.2f}s')

    # MVP média impacto
    # calcula MVP manualmente
    mvp=None; mvp_med=0
    for h in ta+tb:
        media_h=(h.dano+h.cura)/(h.acts or 1)
        if (mvp is None) or (media_h>mvp_med): mvp=h; mvp_med=media_h

    def lista(ts):
        for h in ts:
            med=(h.dano+h.cura)/(h.acts or 1)
            print(f'  {h.nome:14} Role={h.funcao:8} HP={max(0,h.hp):5.0f} Dano={h.dano:5.0f} Cura={h.cura:5.0f} Kills={h.k} Acoes={h.acts} Ults={h.ults} Media={med:5.2f}')

    print('\n===== ESTATISTICAS =====')
    if ven=='A':
        print('Time A (Vencedor):')
        lista(ordenar_por_total(ta))
        print('Time B:')
        lista(ordenar_por_total(tb))
    elif ven=='B':
        print('Time B (Vencedor):')
        lista(ordenar_por_total(tb))
        print('Time A:')
        lista(ordenar_por_total(ta))
    else:
        print('Time A:')
        lista(ordenar_por_total(ta))
        print('Time B:')
        lista(ordenar_por_total(tb))

    if mvp:
        origem='A' if mvp in ta else 'B'
        print('\n===== MVP DETALHES =====')
        info={'nome':mvp.nome,'funcao':mvp.funcao,'idade':mvp.idade,'fraseUlt':mvp.frase,'time':origem,'dano_total':int(mvp.dano),'cura_total':int(mvp.cura),'kills':mvp.k,'acoes':mvp.acts,'ultimates':mvp.ults,'media_impacto':round(mvp_med,2)}
        try: print(json.dumps(info,ensure_ascii=False,indent=2))
        except: print(info)
        print(f'<< {mvp.nome} FOI O MVP >>')

    print('\nPartida encerrada. Esperando mais herois...')
    with lock:
        in_match = False


def main():
    cfg=dict(host=os.getenv('RABBITMQ_HOST','localhost'),port=int(os.getenv('RABBITMQ_PORT','5672')),user=os.getenv('RABBITMQ_USER','guest'),password=os.getenv('RABBITMQ_PASSWORD','guest'),vhost=os.getenv('RABBITMQ_VHOST','/'),queue=os.getenv('HEROI_QUEUE','overwatch_herois'),exchange=os.getenv('HEROI_EXCHANGE'),exchange_type=os.getenv('HEROI_EXCHANGE_TYPE','direct'),routing_key=os.getenv('HEROI_ROUTING_KEY','#'),prefetch=int(os.getenv('RABBITMQ_PREFETCH','10')),reconnect=int(os.getenv('RABBITMQ_RECONNECT_DELAY','5')))
    threading.Thread(target=consumidor,args=(cfg,),daemon=True).start(); print('Esperando herois (>=6 inicia partida)... Ctrl+C para sair')
    try:
        while not stop_evt.is_set(): time.sleep(0.5)
    except KeyboardInterrupt:
        print('Saindo...'); stop_evt.set()


if __name__=='__main__': random.seed(); main()
