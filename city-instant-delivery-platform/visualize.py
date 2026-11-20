"""
Visualization module for City Instant Service Platform.
Provides: path visualization, scheduling process visualization, simulation visualization.
"""
import matplotlib.pyplot as plt
import matplotlib
import matplotlib.patches as mpatches
from matplotlib.lines import Line2D
import networkx as nx
import numpy as np

matplotlib.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
matplotlib.rcParams['axes.unicode_minus'] = False


def _build_networkx_graph(graph):
    """Convert our Graph to a networkx Graph for layout computation."""
    G = nx.Graph()
    for node in graph.get_nodes():
        G.add_node(node)
    for u in graph.adj:
        for v, w in graph.adj[u].items():
            if u < v:
                G.add_edge(u, v, weight=w)
    return G


def _get_layout(G, seed=42):
    """Get a stable spring layout for the graph."""
    return nx.spring_layout(G, seed=seed, k=1.5/np.sqrt(len(G.nodes())))


def visualize_path(graph, src, dst, path, cost, filename="path_visualization.png"):
    """
    Visualize city network and highlight shortest path.

    Args:
        graph: our Graph object
        src, dst: source and destination nodes
        path: list of nodes in shortest path
        cost: total path cost
        filename: output file
    """
    G = _build_networkx_graph(graph)
    pos = _get_layout(G)

    fig, ax = plt.subplots(1, 1, figsize=(10, 8))

    nx.draw_networkx_edges(G, pos, ax=ax, edge_color='#CCCCCC', width=1.0, alpha=0.7)

    edge_labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=ax,
                                  font_size=7, font_color='#666666')

    node_colors = []
    for node in G.nodes():
        if node == src:
            node_colors.append('#2ECC71')
        elif node == dst:
            node_colors.append('#E74C3C')
        else:
            node_colors.append('#5DADE2')
    nx.draw_networkx_nodes(G, pos, ax=ax, node_color=node_colors,
                           node_size=400, edgecolors='#333333', linewidths=1.2)
    nx.draw_networkx_labels(G, pos, ax=ax, font_size=9, font_weight='bold')

    if path and len(path) > 1:
        path_edges = list(zip(path[:-1], path[1:]))
        nx.draw_networkx_edges(G, pos, edgelist=path_edges, ax=ax,
                               edge_color='#E74C3C', width=3.5, alpha=0.9,
                               style='solid')

    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#2ECC71',
               markersize=12, label=f'Source (node {src})'),
        Line2D([0], [0], marker='o', color='w', markerfacecolor='#E74C3C',
               markersize=12, label=f'Destination (node {dst})'),
        Line2D([0], [0], color='#E74C3C', linewidth=3, label=f'Shortest path (cost={cost})'),
    ]
    ax.legend(handles=legend_elements, loc='upper left', fontsize=10)
    ax.set_title(f"City Network & Shortest Path: {src} -> {dst}\nPath: {' -> '.join(map(str, path))}",
                 fontsize=13, fontweight='bold')
    ax.axis('off')
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()
    return filename


def visualize_scheduling(scheduler, current_time, filename="scheduling_visualization.png"):
    """
    Visualize order scheduling process.
    Left: priority factor breakdown for each order.
    Right: order assignment timeline (Gantt-style).

    Args:
        scheduler: Scheduler object with orders loaded
        current_time: current simulation time for priority calculation
        filename: output file
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

    # --- Left: Priority factor breakdown ---
    orders = [(oid, o) for oid, o in scheduler.orders.items() if o.status == "pending"]
    if not orders:
        orders = list(scheduler.orders.items())

    orders_sorted = sorted(orders, key=lambda x: scheduler._compute_priority(x[1]))

    oids = []
    urgency_scores = []
    amount_scores = []
    wait_scores = []
    cost_scores = []

    w1, w2, w3, w4 = scheduler.weights
    for oid, order in orders_sorted:
        oids.append(f"O{oid}")
        urgency_scores.append(w1 * order.urgency / 5.0)
        amount_scores.append(w2 * min(order.amount / 100.0, 1.0))
        wait_time = max(current_time - order.create_time, 0)
        wait_scores.append(w3 * min(wait_time / 30.0, 1.0))
        cost = min(order.path_cost / 50.0, 1.0) if order.path_cost != float('inf') else 1.0
        cost_scores.append(w4 * cost)

    y_pos = np.arange(len(oids))
    bar_height = 0.6

    bars1 = ax1.barh(y_pos, urgency_scores, bar_height, label=f'Urgency (w={w1})', color='#E74C3C')
    bars2 = ax1.barh(y_pos, amount_scores, bar_height, left=urgency_scores,
                     label=f'Amount (w={w2})', color='#F39C12')
    left2 = [a + b for a, b in zip(urgency_scores, amount_scores)]
    bars3 = ax1.barh(y_pos, wait_scores, bar_height, left=left2,
                     label=f'Wait Time (w={w3})', color='#3498DB')
    left3 = [a + b for a, b in zip(left2, wait_scores)]
    bars4 = ax1.barh(y_pos, cost_scores, bar_height, left=left3,
                     label=f'-Path Cost (w={w4})', color='#95A5A6', alpha=0.6)

    ax1.set_yticks(y_pos)
    ax1.set_yticklabels(oids)
    ax1.set_xlabel('Priority Score Components')
    ax1.set_title('Order Priority Breakdown\n(higher total = higher priority)', fontweight='bold')
    ax1.legend(loc='lower right', fontsize=9)
    ax1.invert_yaxis()

    # --- Right: Assignment timeline (Gantt Chart) ---
    assigned_orders = [(oid, o) for oid, o in scheduler.orders.items()
                       if o.assigned_time is not None]

    if assigned_orders:
        courier_ids = sorted(set(o.courier_id for _, o in assigned_orders if o.courier_id is not None))
        courier_y = {cid: i for i, cid in enumerate(courier_ids)}
        gantt_colors = ['#E74C3C', '#3498DB', '#2ECC71', '#9B59B6', '#F39C12',
                        '#1ABC9C', '#E67E22', '#8E44AD', '#16A085', '#D35400']

        for idx, (oid, order) in enumerate(assigned_orders):
            if order.courier_id is None:
                continue
            y = courier_y[order.courier_id]
            start = order.assigned_time
            duration = (order.complete_time - order.assigned_time) if order.complete_time else 10
            color = gantt_colors[idx % len(gantt_colors)]
            ax2.barh(y, duration, left=start, height=0.5, color=color,
                     edgecolor='#333', linewidth=0.8, alpha=0.85)
            ax2.text(start + duration / 2, y, f'O{oid}', ha='center', va='center',
                     fontsize=8, fontweight='bold', color='white')

        ax2.set_yticks(range(len(courier_ids)))
        ax2.set_yticklabels([f'Courier {cid}' for cid in courier_ids])
        ax2.set_xlabel('Time Step')
        ax2.set_title('Order Assignment Timeline\n(Gantt Chart)', fontweight='bold')
        ax2.grid(axis='x', alpha=0.3, linestyle='--')
        ax2.set_axisbelow(True)
    else:
        all_orders = sorted(scheduler.orders.values(), key=lambda o: o.create_time)
        for i, order in enumerate(all_orders):
            color = '#E74C3C' if order.urgency >= 4 else '#F39C12' if order.urgency >= 3 else '#3498DB'
            ax2.scatter(order.create_time, i, c=color, s=60, zorder=3)
            ax2.hlines(i, order.create_time, order.deadline, colors='#CCCCCC',
                       linewidth=1, linestyles='dashed')
        ax2.set_xlabel('Time')
        ax2.set_ylabel('Order Index')
        ax2.set_title('Order Arrival & Deadline Timeline', fontweight='bold')
        legend_elements = [
            Line2D([0], [0], marker='o', color='w', markerfacecolor='#E74C3C',
                   markersize=8, label='Urgency 4-5'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor='#F39C12',
                   markersize=8, label='Urgency 3'),
            Line2D([0], [0], marker='o', color='w', markerfacecolor='#3498DB',
                   markersize=8, label='Urgency 1-2'),
            Line2D([0], [0], color='#CCCCCC', linestyle='dashed', label='Deadline'),
        ]
        ax2.legend(handles=legend_elements, loc='upper right', fontsize=9)

    plt.suptitle(f"Order Scheduling Visualization (t={current_time})", fontsize=14, fontweight='bold')
    plt.tight_layout()
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()
    return filename


def visualize_simulation(graph, history, filename="simulation_visualization.png"):
    """
    Visualize simulation process with snapshots and metric curves.

    Args:
        graph: our Graph object
        history: list of dicts from Simulator.history, each with:
            - time: int
            - courier_positions: {courier_id: node}
            - courier_status: {courier_id: 'idle'/'delivering'}
            - pending_count: int
            - completed_count: int
            - timeout_count: int
            - active_paths: [(courier_id, path_remaining)]
        filename: output file
    """
    G = _build_networkx_graph(graph)
    pos = _get_layout(G)

    total_steps = len(history)
    # Pick 6 key frames evenly spaced
    num_frames = 6
    indices = [int(i * (total_steps - 1) / (num_frames - 1)) for i in range(num_frames)]
    indices = sorted(set(indices))
    num_frames = len(indices)

    fig = plt.figure(figsize=(18, 14))

    # Top: 6 snapshots in 2 rows of 3
    gs = fig.add_gridspec(3, 3, hspace=0.35, wspace=0.25)

    courier_colors = plt.cm.tab10(np.linspace(0, 1, 10))

    for frame_idx, hist_idx in enumerate(indices):
        row = frame_idx // 3
        col = frame_idx % 3
        ax = fig.add_subplot(gs[row, col])

        snapshot = history[hist_idx]
        t = snapshot['time']

        nx.draw_networkx_edges(G, pos, ax=ax, edge_color='#DDDDDD', width=0.8, alpha=0.6)

        nx.draw_networkx_nodes(G, pos, ax=ax, node_color='#D5D8DC',
                               node_size=120, edgecolors='#999', linewidths=0.5)

        for cid, cpos in snapshot['courier_positions'].items():
            if cpos in pos:
                color = courier_colors[cid % 10]
                is_delivering = snapshot['courier_status'].get(cid) == 'delivering'
                marker = '^' if is_delivering else 'o'
                size = 200 if is_delivering else 150
                ax.scatter(*pos[cpos], c=[color], s=size, marker=marker,
                          zorder=5, edgecolors='black', linewidths=1.0)

        for cid, path_rem in snapshot.get('active_paths', []):
            if len(path_rem) >= 2:
                color = courier_colors[cid % 10]
                path_edges = list(zip(path_rem[:-1], path_rem[1:]))
                valid_edges = [(u, v) for u, v in path_edges if u in pos and v in pos]
                if valid_edges:
                    nx.draw_networkx_edges(G, pos, edgelist=valid_edges, ax=ax,
                                           edge_color=[color], width=2.0, alpha=0.7,
                                           style='dashed')

        ax.set_title(f"t={t}  |  Pending:{snapshot['pending_count']}  "
                     f"Done:{snapshot['completed_count']}  Timeout:{snapshot['timeout_count']}",
                     fontsize=9)
        ax.axis('off')

    # Bottom row: metric curves
    ax_curve = fig.add_subplot(gs[2, :])
    times = [h['time'] for h in history]
    completed = [h['completed_count'] for h in history]
    timeout = [h['timeout_count'] for h in history]
    pending = [h['pending_count'] for h in history]

    ax_curve.plot(times, completed, color='#2ECC71', linewidth=2, label='Completed (cumulative)')
    ax_curve.plot(times, timeout, color='#E74C3C', linewidth=2, label='Timeout (cumulative)')
    ax_curve.plot(times, pending, color='#F39C12', linewidth=1.5, linestyle='--', label='Pending (current)')
    ax_curve.fill_between(times, completed, alpha=0.1, color='#2ECC71')
    ax_curve.fill_between(times, timeout, alpha=0.1, color='#E74C3C')
    ax_curve.set_xlabel('Time Step', fontsize=11)
    ax_curve.set_ylabel('Count', fontsize=11)
    ax_curve.set_title('Simulation Metrics Over Time', fontsize=12, fontweight='bold')
    ax_curve.legend(loc='upper left', fontsize=10)
    ax_curve.grid(True, alpha=0.3)

    legend_elements = [
        Line2D([0], [0], marker='o', color='w', markerfacecolor='gray',
               markersize=8, label='Idle Courier'),
        Line2D([0], [0], marker='^', color='w', markerfacecolor='gray',
               markersize=8, label='Delivering Courier'),
    ]
    fig.legend(handles=legend_elements, loc='upper right', fontsize=10,
               bbox_to_anchor=(0.98, 0.98))

    plt.suptitle("Simulation Process Visualization", fontsize=15, fontweight='bold', y=0.99)
    plt.savefig(filename, dpi=150, bbox_inches='tight')
    plt.close()
    return filename