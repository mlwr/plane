import json, ast, re, sys, collections
D = json.load(open(sys.argv[1]))
# add DefaultRouter v1 entries
for cls, base, file, acts, pc in [("WorkspaceInvitationsViewset","/api/v1/workspaces/<str:slug>/invitations/","api/views/invite.py",["list","create","retrieve","partial_update","destroy"],"[WorkspaceOwnerPermission]"),
                                  ("StickyViewSet","/api/v1/workspaces/<str:slug>/stickies/","api/views/sticky.py",["list","create","retrieve","partial_update","destroy"],"[WorkspaceUserPermission]")]:
    for a in acts:
        http = {"list":"GET","create":"POST","retrieve":"GET","partial_update":"PATCH","destroy":"DELETE"}[a]
        route = base if a in ("list","create") else base + "<uuid:pk>/"
        D.append({"area":"api","route":route,"http":http,"class":cls,"action":a,"file":file,"line":None,"perm_classes":pc,"perm_from":cls,"decorators":[],"get_permissions":False})

R = {}  # class -> resource
def m(res, *names):
    for n in names: R[n] = res
# ---- instance
m("instance","InstanceEndpoint"); m("instance_admin","InstanceAdminEndpoint","InstanceAdminUserMeEndpoint","InstanceAdminUserSessionEndpoint")
m("instance_auth_legacy","InstanceAdminSignOutEndpoint","InstanceAdminSignInEndpoint","InstanceAdminSignUpEndpoint","SignUpScreenVisitedEndpoint")
m("instance_configuration","InstanceConfigurationEndpoint","DisableEmailFeatureEndpoint","EmailCredentialCheckEndpoint")
m("instance_workspace","InstanceWorkSpaceAvailabilityCheckEndpoint","InstanceWorkSpaceEndpoint")
# ---- user self
m("user","UserEndpoint","UserSessionEndpoint","UpdateUserOnBoardedEndpoint","UpdateUserTourCompletedEndpoint","UserWorkSpacesEndpoint","UserLastProjectWithWorkspaceEndpoint")
m("user_profile","ProfileEndpoint"); m("user_account","AccountEndpoint")
m("user_activity","UserActivityEndpoint","UserActivityGraphEndpoint","UserIssueCompletedGraphEndpoint","UserWorkspaceDashboardEndpoint")
m("api_token","ApiTokenEndpoint"); m("user_asset","UserAssetsEndpoint","UserAssetsV2Endpoint","UserAssetEndpoint","UserServerAssetEndpoint","FileAssetEndpoint","FileAssetViewSet")
m("notification","NotificationViewSet","UnreadNotificationEndpoint","MarkAllReadNotificationViewSet")
m("notification_preference","UserNotificationPreferenceEndpoint")
m("timezone","TimezoneEndpoint"); m("unsplash","UnsplashEndpoint")
# ---- workspace
m("workspace","WorkSpaceViewSet","WorkSpaceAvailabilityCheckEndpoint")
m("workspace_member","WorkSpaceMemberViewSet","WorkspaceMemberUserEndpoint","WorkspaceMemberAPIEndpoint","WorkspaceMemberLiteAPIEndpoint","WorkspaceProjectMemberEndpoint")
m("workspace_member_preference","WorkspaceMemberUserViewsEndpoint","WorkspaceUserPropertiesEndpoint","WorkspaceUserPreferenceViewSet","WorkspaceHomePreferenceViewSet")
m("workspace_invitation","WorkspaceInvitationsViewset","UserWorkspaceInvitationsViewSet","WorkspaceJoinEndpoint")
m("workspace_theme","WorkspaceThemeViewSet")
m("workspace_profile","WorkspaceUserProfileStatsEndpoint","WorkspaceUserActivityEndpoint","ExportWorkspaceUserActivityEndpoint","WorkspaceUserProfileEndpoint","WorkspaceUserProfileIssuesEndpoint")
m("workspace_metadata","WorkspaceLabelsEndpoint","WorkspaceStatesEndpoint","WorkspaceEstimatesEndpoint","WorkspaceModulesEndpoint","WorkspaceCyclesEndpoint")
m("favorite","WorkspaceFavoriteEndpoint","WorkspaceFavoriteGroupEndpoint","ProjectFavoritesViewSet","CycleFavoriteViewSet","ModuleFavoriteViewSet","IssueViewFavoriteViewSet","PageFavoriteViewSet")
m("draft_work_item","WorkspaceDraftIssueViewSet")
m("quick_link","QuickLinkViewSet"); m("recent_visit","UserRecentVisitViewSet"); m("sticky","WorkspaceStickyViewSet","StickyViewSet")
m("webhook","WebhookEndpoint","WebhookSecretRegenerateEndpoint","WebhookLogsEndpoint")
m("analytics","AnalyticsEndpoint","SavedAnalyticEndpoint","ExportAnalyticsEndpoint","DefaultAnalyticsEndpoint","ProjectStatsEndpoint","AdvanceAnalyticsEndpoint","AdvanceAnalyticsStatsEndpoint","AdvanceAnalyticsChartEndpoint")
m("analytic_view","AnalyticViewViewset")
m("project_analytics","ProjectAdvanceAnalyticsEndpoint","ProjectAdvanceAnalyticsStatsEndpoint","ProjectAdvanceAnalyticsChartEndpoint")
m("export","ExportIssuesEndpoint")
m("workspace_asset","WorkspaceFileAssetEndpoint","AssetRestoreEndpoint","AssetCheckEndpoint","DuplicateAssetEndpoint","WorkspaceAssetDownloadEndpoint","GenericAssetEndpoint","StaticFileAssetEndpoint")
m("workspace_view","WorkspaceViewViewSet","WorkspaceViewIssuesViewSet")
m("search","GlobalSearchEndpoint","SearchEndpoint","IssueSearchEndpoint")
m("ai_assistant","GPTIntegrationEndpoint","WorkspaceGPTIntegrationEndpoint")
m("workspace_work_item","WorkspaceIssueAPIEndpoint")
# ---- project
m("project","ProjectViewSet","ProjectListCreateAPIEndpoint","ProjectListLiteAPIEndpoint","ProjectDetailAPIEndpoint","ProjectSummaryAPIEndpoint","ProjectIdentifierEndpoint","ProjectArchiveUnarchiveEndpoint","ProjectArchiveUnarchiveAPIEndpoint","UserProjectRolesEndpoint")
m("project_member","ProjectMemberViewSet","ProjectMemberUserEndpoint","ProjectMemberListCreateAPIEndpoint","ProjectMemberDetailAPIEndpoint","ProjectMemberLiteAPIEndpoint")
m("project_member_preference","ProjectUserViewsEndpoint","ProjectMemberPreferenceEndpoint","ProjectUserDisplayPropertyEndpoint","CycleUserPropertiesEndpoint","ModuleUserPropertiesEndpoint")
m("project_invitation","ProjectInvitationsViewset","UserProjectInvitationsViewset","ProjectJoinEndpoint")
m("project_publish","DeployBoardViewSet")
m("state","StateViewSet","StateListCreateAPIEndpoint","StateDetailAPIEndpoint","IntakeStateEndpoint")
m("label","LabelViewSet","BulkCreateIssueLabelsEndpoint","LabelListCreateAPIEndpoint","LabelDetailAPIEndpoint")
m("estimate","ProjectEstimatePointEndpoint","BulkEstimatePointEndpoint","EstimatePointEndpoint","ProjectEstimateAPIEndpoint","EstimatePointListCreateAPIEndpoint","EstimatePointDetailAPIEndpoint")
m("work_item","IssueListEndpoint","IssueViewSet","IssueDetailEndpoint","IssuePaginatedViewSet","BulkDeleteIssuesEndpoint","BulkArchiveIssuesEndpoint","IssueArchiveViewSet","DeletedIssuesListViewSet","IssueBulkUpdateDateEndpoint","IssueMetaEndpoint","IssueDetailIdentifierEndpoint","SubIssuesEndpoint",
  "IssueListCreateAPIEndpoint","IssueDetailAPIEndpoint")
m("work_item_link","IssueLinkViewSet","IssueLinkListCreateAPIEndpoint","IssueLinkDetailAPIEndpoint")
m("work_item_attachment","IssueAttachmentEndpoint","IssueAttachmentV2Endpoint","IssueAttachmentListCreateAPIEndpoint","IssueAttachmentDetailAPIEndpoint")
m("work_item_activity","IssueActivityEndpoint","IssueActivityListAPIEndpoint","IssueActivityDetailAPIEndpoint","IssueVersionEndpoint","WorkItemDescriptionVersionEndpoint","IntakeWorkItemDescriptionVersionEndpoint")
m("work_item_comment","IssueCommentViewSet","IssueCommentListCreateAPIEndpoint","IssueCommentDetailAPIEndpoint")
m("work_item_subscription","IssueSubscriberViewSet")
m("work_item_reaction","IssueReactionViewSet","CommentReactionViewSet")
m("work_item_relation","IssueRelationViewSet","IssueRelationListCreateAPIEndpoint")
m("cycle","CycleViewSet","CycleDateCheckEndpoint","CycleArchiveUnarchiveEndpoint","CycleProgressEndpoint","CycleAnalyticsEndpoint","CycleListCreateAPIEndpoint","CycleListLiteAPIEndpoint","CycleDetailAPIEndpoint","CycleArchiveUnarchiveAPIEndpoint")
m("cycle_work_item","CycleIssueViewSet","TransferCycleIssueEndpoint","CycleIssueListCreateAPIEndpoint","CycleIssueDetailAPIEndpoint","TransferCycleIssueAPIEndpoint")
m("module","ModuleViewSet","ModuleArchiveUnarchiveEndpoint","ModuleListCreateAPIEndpoint","ModuleListLiteAPIEndpoint","ModuleDetailAPIEndpoint","ModuleArchiveUnarchiveAPIEndpoint","ModuleLinkViewSet")
m("module_work_item","ModuleIssueViewSet","ModuleIssueListCreateAPIEndpoint","ModuleIssueDetailAPIEndpoint")
m("intake","IntakeViewSet"); m("intake_work_item","IntakeIssueViewSet","IntakeIssueListCreateAPIEndpoint","IntakeIssueDetailAPIEndpoint")
m("page","PageViewSet","PagesDescriptionViewSet","PageDuplicateEndpoint"); m("page_version","PageVersionEndpoint")
m("view","IssueViewViewSet")
m("project_asset","ProjectAssetEndpoint","ProjectBulkAssetEndpoint","ProjectAssetDownloadEndpoint")
# ---- space
m("public_board","WorkspaceProjectDeployBoardEndpoint","IssueRetrievePublicEndpoint","ProjectMetaDataEndpoint","ProjectDeployBoardPublicSettingsEndpoint","ProjectIssuesPublicEndpoint","WorkspaceProjectAnchorEndpoint","ProjectCyclesEndpoint","ProjectModulesEndpoint","ProjectStatesEndpoint","ProjectLabelsEndpoint","ProjectMembersEndpoint")
m("public_asset","EntityAssetEndpoint","EntityBulkAssetEndpoint")
m("public_intake","IntakeIssuePublicViewSet"); m("public_comment","IssueCommentPublicViewSet")
m("public_reaction","IssueReactionPublicViewSet","CommentReactionPublicViewSet"); m("public_vote","IssueVotePublicViewSet")

VERB = {"list":"read","retrieve":"read","get":"read","summary":"read","list_detail":"read",
        "create":"create","post":"create","update":"update","partial_update":"update","patch":"update","put":"update",
        "destroy":"delete","delete":"delete","archive":"archive","unarchive":"archive","lock":"lock","unlock":"lock",
        "access":"change_access","subscribe":"subscribe","unsubscribe":"subscribe","subscription_status":"read",
        "mark_read":"update","mark_unread":"update","leave":"leave","mark_as_default":"update","remove_relation":"delete",
        "create_draft_to_issue":"convert","restore":"update","create_issue_modules":"create","create_module_issues":"create",
        "deactivate":"deactivate","generate_email_verification_code":"change_email","update_email":"change_email",
        "retrieve_instance_admin":"read","retrieve_user_settings":"read"}

def scope_of(x):
    a, r = x["area"], x["route"]
    if a == "license": return "instance"
    if a == "space": return "public"
    if "/projects/<" in r or "/project_id" in r: return "project"
    if "workspaces/<str:slug>" in r: return "workspace"
    return "user"

def roles(s):
    mp={"ROLE.ADMIN":"A","ROLE.MEMBER":"M","ROLE.GUEST":"G","ADMIN":"A","MEMBER":"M","GUEST":"G","20":"A","15":"M","5":"G"}
    return sorted({mp[t] for t in s}, key=lambda c:"AMG".index(c))

def parse_dec(s):
    t = ast.parse(s).body[0].value
    kw = {k.arg: ast.unparse(k.value) for k in t.keywords}
    rl = ast.unparse(t.args[0]) if t.args else kw.get("allowed_roles","[]")
    items = [i.strip() for i in rl.strip("[]").split(",") if i.strip()]
    level = kw.get("level","'PROJECT'").strip("'\"")
    creator = kw.get("creator","False") == "True"
    model = kw.get("model")
    rs = roles(items)
    base = (f"WS({','.join(rs)})" if level=="WORKSPACE" else f"PRJ+({','.join(rs)})") if rs else "–"
    if creator: base = (base + " ∨ " if rs else "") + f"Creator({model})"
    return base

SAFE = {"GET","HEAD","OPTIONS"}
def cls_req(pc, http, cls):
    # get_permissions overrides
    if cls == "IssueSubscriberViewSet": return None
    if cls in ("EntityAssetEndpoint",): return "Anon" if http=="GET" else "Auth"
    if cls == "IssueCommentPublicViewSet": return "Anon" if http=="GET" else "Auth"
    if cls == "ProjectMemberListCreateAPIEndpoint" or cls=="ProjectMemberDetailAPIEndpoint":
        pass
    if cls in ("LabelListCreateAPIEndpoint","LabelDetailAPIEndpoint"):
        return "PRJ(A,M,G)" if http in SAFE else "PRJ+(A)"
    if cls in ("StateListCreateAPIEndpoint","StateDetailAPIEndpoint"):
        return "PRJ(A,M,G)" if http in SAFE else "PRJ+(A)"
    if cls == "InstanceEndpoint": return "INST" if http=="PATCH" else "Anon"
    if pc is None: return "Auth"
    p = pc.strip("[]() ").replace(" ","")
    parts = [q for q in p.split(",") if q]
    out=[]
    for q in parts:
        if q == "IsAuthenticated": continue
        out.append(single(q, http))
    if not out: return "Auth" if "IsAuthenticated" in parts or not parts else "Auth"
    return " ∧ ".join(out)

def single(q, http):
    if q == "AllowAny": return "Anon"
    if q == "WorkSpaceBasePermission": return "Auth" if http in SAFE|{"POST"} else "WS(A)"
    if q == "WorkspaceOwnerPermission": return "WS(A)"
    if q == "WorkSpaceAdminPermission": return "WS(A,M)"
    if q == "WorkspaceEntityPermission": return "WS(A,M,G)" if http in SAFE else "WS(A,M)"
    if q in ("WorkspaceViewerPermission","WorkspaceUserPermission","WorkspaceMemberPermission"): return "WS(A,M,G)"
    if q == "ProjectBasePermission": return "WS(A,M,G)" if http in SAFE else ("WS(A,M)" if http=="POST" else "PRJ+(A)")
    if q in ("ProjectMemberPermission","ProjectEntityPermission"): return "PRJ(A,M,G)" if http in SAFE else "PRJ(A,M)"
    if q == "ProjectAdminPermission": return "PRJ+(A)"
    if q == "ProjectLitePermission": return "PRJ(A,M,G)"
    if q == "ProjectPagePermission": return {"POST":"PAGE(A,M)","GET":"PAGE(A,M,G)","PATCH":"PAGE(A,M)","PUT":"PAGE(A,M)","DELETE":"PAGE(A)"}[http]
    if q == "InstanceAdminPermission": return "INST"
    return "?"+q

rows=[]
for x in D:
    cls = x["class"]; http = x["http"]
    cr = cls_req(x["perm_classes"], http, cls)
    if cls == "IssueSubscriberViewSet":
        cr = "PRJ(A,M,G)" if x["action"] in ("subscribe","unsubscribe","subscription_status") else ("PRJ(A,M,G)" if http in SAFE else "PRJ(A,M)")
    if cls == "ProjectMemberListCreateAPIEndpoint" or cls == "ProjectMemberDetailAPIEndpoint":
        cr = "PRJ(A,M,G)" if http=="GET" else "PRJ+(A)"
    decs = [parse_dec(d) for d in x["decorators"] if d.startswith("allow_permission")]
    other = [d for d in x["decorators"] if not d.startswith("allow_permission")]
    req = cr
    if decs:
        req = decs[0] if cr in ("Auth",) else f"{cr} ∧ {decs[0]}"
    res = R.get(cls, "?"+cls)
    verb = VERB.get(x["action"], x["action"])
    if res in ("instance_auth_legacy",): verb = x["action"]
    key = f"{scope_of(x)}.{res}.{verb}" if not res.startswith("public") else f"public.{res[7:]}.{verb}"
    if scope_of(x)=="instance": key=f"instance.{res.replace('instance_','') if res!='instance' else 'settings'}.{verb}"
    rows.append({**x, "req": req, "key": key, "other_decorators": other})
json.dump(rows, open(sys.argv[2],"w"), indent=1, ensure_ascii=False)
unk=[r for r in rows if "?" in r["key"] or "?" in r["req"]]
print("rows",len(rows),"unknown",len(unk))
for u in unk[:30]: print(u["class"],u["key"],u["req"])
