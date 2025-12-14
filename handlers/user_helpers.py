# -*- coding: utf-8 -*-

# Общие вспомогательные функции для UserPie

def clear_fsm(context):
    """
    Аккуратно очищает FSM пользователя,
    не трогая накопленные инсайты.
    """
    keys_to_remove = []
    for key in context.user_data.keys():
        if key.startswith(("pm_", "ta_", "ns_", "growth", "premium")):
            keys_to_remove.append(key)

    for key in keys_to_remove:
        context.user_data.pop(key, None)


def save_insights(
    context,
    last_scenario=None,
    last_verdict=None,
    risk_level=None,
    demand_type=None,
    seasonality=None,
    competition=None,
    resource=None,
):
    """
    Сохраняет краткий итог последнего сценария
    для использования в bridge / истории.
    """
    insights = context.user_data.get("insights", {})

    if last_scenario is not None:
        insights["scenario"] = last_scenario
    if last_verdict is not None:
        insights["verdict"] = last_verdict
    if risk_level is not None:
        insights["risk"] = risk_level
    if demand_type is not None:
        insights["demand"] = demand_type
    if seasonality is not None:
        insights["seasonality"] = seasonality
    if competition is not None:
        insights["competition"] = competition
    if resource is not None:
        insights["resource"] = resource

    context.user_data["insights"] = insights


def insights_bridge_text(context):
    """
    Короткий bridge перед новым сценарием,
    если есть сохранённые инсайты.
    """
    insights = context.user_data.get("insights")
    if not insights:
        return ""

    parts = ["📌 Что уже зафиксировали:\n"]
    if insights.get("scenario"):
        parts.append(f"• Сценарий: {insights['scenario']}")
    if insights.get("verdict"):
        parts.append(f"• Вердикт: {insights['verdict']}")
    if insights.get("risk"):
        parts.append(f"• Риск: {insights['risk']}")

    return "\n".join(parts) + "\n\n"

# =============================
# RESULTS STORAGE (ARCH LAYER)
# =============================

def save_result(context, result: dict):
    """
    Сохраняет завершённый результат сценария.
    Используется ТОЛЬКО в *_finish шагах FSM.
    """
    history = context.user_data.get("history", [])
    history.append(result)
    context.user_data["history"] = history


def get_results_summary(context):
    """
    Возвращает краткую сводку для личного кабинета (FREE).
    """
    history = context.user_data.get("history", [])
    summary = {}

    for item in history:
        t = item.get("type")
        summary[t] = summary.get(t, 0) + 1

    return summary

