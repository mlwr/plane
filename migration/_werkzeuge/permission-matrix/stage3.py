import json, re, sys, collections
rows = json.load(open(sys.argv[1]))
SAFE={"GET","HEAD","OPTIONS"}

# ---------- key refinement (verb/resource overrides) ----------
def refine(r):
    c, a, h, k = r["class"], r["action"], r["http"], r["key"]
    sc, res, verb = k.split(".")
    if "ArchiveUnarchive" in c:
        verb = {"GET":"read_archived","POST":"archive","DELETE":"unarchive"}[h]
    if c == "IssueArchiveViewSet":
        verb = {"list":"read_archived","retrieve":"read_archived","archive":"archive","unarchive":"unarchive"}[a]
    if c == "BulkArchiveIssuesEndpoint": verb = "archive"
    if c == "PageViewSet" and a in ("unarchive","unlock"): verb = a
    if c in ("CycleViewSet","ModuleViewSet") and a == "retrieve": verb = "read_detail"
    if c == "ProjectEstimatePointEndpoint": verb = "read_points"
    if c == "ModuleLinkViewSet": res = "module_link"
    if c == "ProjectSummaryAPIEndpoint": verb = "read_summary"
    if c in ("ProjectAdvanceAnalyticsChartEndpoint",): verb = "read_charts"
    if c in ("DefaultAnalyticsEndpoint","ProjectStatsEndpoint"): verb = "read_basic"
    if c == "ProjectIdentifierEndpoint": sc, res, verb = "workspace","project", ("check_identifier" if h=="GET" else "release_identifier")
    if c == "ProjectAnalyticsEndpoint": pass
    fav = {"CycleFavoriteViewSet":"cycle","ModuleFavoriteViewSet":"module","IssueViewFavoriteViewSet":"view","PageFavoriteViewSet":"page","ProjectFavoritesViewSet":"project"}
    if c in fav:
        res = fav[c]; verb = "favorite"; sc = "project" if c!="ProjectFavoritesViewSet" else "workspace"
    if c == "WorkspaceFavoriteEndpoint" or c=="WorkspaceFavoriteGroupEndpoint": sc,res,verb = "workspace","favorite",{"GET":"read","POST":"create","PATCH":"update","DELETE":"delete"}[h]
    if res == "project_analytics": res = "analytics"
    if c in ("CycleDateCheckEndpoint",): verb = "create"
    if c == "TransferCycleIssueEndpoint" or c=="TransferCycleIssueAPIEndpoint": verb = "transfer"
    if c == "IssueBulkUpdateDateEndpoint": verb = "update"
    if c == "DeletedIssuesListViewSet": verb = "read"
    if c == "UserProjectRolesEndpoint": sc,res,verb = "workspace","project","read"
    if c in ("WorkSpaceAvailabilityCheckEndpoint",): sc,res,verb="user","workspace","create"
    if c == "WorkspaceProjectMemberEndpoint": sc,res,verb = "workspace","project_member","read"
    if c in ("WorkspaceViewIssuesViewSet",): verb="read"
    if c in ("ExportWorkspaceUserActivityEndpoint",): verb="export"
    if c == "WorkspaceGPTIntegrationEndpoint": sc="workspace"
    if c in ("ProjectUserViewsEndpoint","ProjectMemberPreferenceEndpoint","ProjectUserDisplayPropertyEndpoint","CycleUserPropertiesEndpoint","ModuleUserPropertiesEndpoint"):
        res="member_preference"; verb = "read" if h=="GET" else "update"
    if c in ("WorkspaceMemberUserViewsEndpoint","WorkspaceUserPropertiesEndpoint","WorkspaceUserPreferenceViewSet","WorkspaceHomePreferenceViewSet"):
        res="member_preference"; verb = "read" if h=="GET" else "update"
    if res == "workspace_member": res = "member"
    if res == "project_member": res = "member"
    if res == "workspace_invitation": res = "invitation"
    if res == "project_invitation": res = "invitation"
    if res == "workspace_theme": res = "theme"
    if res == "workspace_profile": res = "member_profile"
    if res == "workspace_metadata": res = "project_metadata"
    if res == "workspace_asset": res = "asset"
    if res == "project_asset": res = "asset"
    if res == "workspace_view": res = "view"
    if res == "workspace_work_item": res = "work_item"
    if res == "project_publish": res = "publish"
    if res == "workspace" and sc=="workspace": res = "settings"
    if c in ("WorkspaceInvitationsViewset",) : sc="workspace"
    if c == "UserWorkspaceInvitationsViewSet": sc,res,verb = "user","invitation","read" if h=="GET" else "accept"
    if c == "UserProjectInvitationsViewset": sc,res,verb = "user","invitation","read" if h=="GET" else "accept"
    if c == "WorkspaceJoinEndpoint": sc,res,verb="public","invitation","read" if h=="GET" else "respond"
    if c == "ProjectJoinEndpoint": sc,res,verb="public","invitation","read" if h=="GET" else "respond"
    if c in ("UserWorkSpacesEndpoint","UserLastProjectWithWorkspaceEndpoint"): sc,res,verb = "user","user","read"
    if c == "WorkSpaceViewSet" and h=="POST": sc,res,verb="user","workspace","create"
    if c == "WorkSpaceViewSet" and h=="GET" and a=="list": sc,res,verb="user","workspace","read"
    if c in ("UserActivityGraphEndpoint","UserIssueCompletedGraphEndpoint","UserWorkspaceDashboardEndpoint"): sc,res,verb="workspace","member_profile","read_own"
    if c == "WorkspaceUserActivityEndpoint" or c=="WorkspaceUserProfileStatsEndpoint" or c=="WorkspaceUserProfileIssuesEndpoint" or c=="WorkspaceUserProfileEndpoint": sc,res,verb="workspace","member_profile","read"
    if c == "UnsplashEndpoint": sc="user"
    if c == "StaticFileAssetEndpoint": sc,res,verb="user","asset","read_static"
    if c in ("NotificationViewSet","UnreadNotificationEndpoint","MarkAllReadNotificationViewSet"):
        sc,res="workspace","notification"
        verb = "read" if h=="GET" else ("delete" if h=="DELETE" else "update")
        if a in ("archive","unarchive"): verb="update"
    if c in ("IntakeWorkItemDescriptionVersionEndpoint",): res="intake_work_item"; verb="read"
    if c in ("WorkItemDescriptionVersionEndpoint","IssueVersionEndpoint"): res="work_item_activity"; verb="read"
    if c in ("IssueSubscriberViewSet",) and a in ("list","create","destroy"): verb = {"list":"read","create":"manage","destroy":"manage"}[a]
    if c in ("CommentReactionViewSet","IssueReactionViewSet"): res="reaction"
    if c in ("IssueDetailIdentifierEndpoint",): sc,res,verb="project","work_item","read"
    if c in ("WorkspaceIssueAPIEndpoint",): sc,res,verb="project","work_item","read"
    if c in ("IssueSearchEndpoint",) and r["area"]=="app": sc,res,verb="project","work_item","search"
    if c in ("IssueSearchEndpoint",) and r["area"]=="api": sc,res,verb="workspace","search","read"
    if c in ("GlobalSearchEndpoint","SearchEndpoint"): sc,res,verb="workspace","search","read"
    if c in ("ExportIssuesEndpoint",): sc,res,verb="workspace","export","read" if h=="GET" else "create"
    if c in ("ExportAnalyticsEndpoint",): verb="export"
    if res in ("user_asset",) : sc="user"
    if c in ("FileAssetEndpoint","FileAssetViewSet"): sc,res = "workspace","asset_legacy"
    if c == "AnalyticViewViewset": res="analytics_view"
    if c in ("ApiTokenEndpoint",): sc="user"
    if c in ("WorkspaceThemeViewSet",): sc="workspace"
    if c == "IntakeStateEndpoint": res,verb="state","read"
    if c in ("SubIssuesEndpoint",): verb = "read" if h=="GET" else "update"
    if c == "BulkCreateIssueLabelsEndpoint": verb="create"
    if c == "BulkDeleteIssuesEndpoint": verb="delete"
    if c in ("PageDuplicateEndpoint",): verb="create"
    if c in ("PagesDescriptionViewSet",): verb = "read" if h=="GET" else "update"
    if c in ("CycleProgressEndpoint","CycleAnalyticsEndpoint"): verb="read"
    if c == "IssueRelationViewSet" and a=="remove_relation": verb="delete"
    if c == "DeployBoardViewSet": res="publish"
    if c == "ProjectMemberViewSet" and a=="leave": verb="leave"
    if c == "WorkSpaceMemberViewSet" and a=="leave": verb="leave"
    if c == "ProjectMemberUserEndpoint": res,verb="member","read_own"
    if c == "WorkspaceMemberUserEndpoint": res,verb="member","read_own"
    if c == "UserRecentVisitViewSet": res="recent_visit"
    if c in ("WorkspaceGPTIntegrationEndpoint","GPTIntegrationEndpoint"): verb="use"
    if c in ("WorkspaceDraftIssueViewSet",) and a=="create_draft_to_issue": verb="convert"
    if c in ("AssetCheckEndpoint",): verb="read"
    if c in ("DuplicateAssetEndpoint",): verb="create"
    if c in ("WorkspaceAssetDownloadEndpoint","ProjectAssetDownloadEndpoint"): verb="read"
    if c in ("AssetRestoreEndpoint",) and r["area"]=="app": verb="update"
    if c == "InstanceAdminUserSessionEndpoint": sc,res,verb="instance","session","read"
    if c == "UserSessionEndpoint": sc,res,verb="user","session","read"
    if c in fav and h=="GET": verb = "read_favorites"
    if c == "UserProjectInvitationsViewset" and h=="POST": sc,res,verb="workspace","project_invitation","accept"
    if r["area"]=="space":
        sc = "public"
        res = res.replace("public_","")
    if c in ("WorkspaceProjectDeployBoardEndpoint",): pass
    return f"{sc}.{res}.{verb}"

# ---------- target requirement overrides (Ziel) ----------
# notation: LEVEL(roles)[+rules]; rules: O=WsAdminOverride, C:<Model>=CreatorBypass, OWN=Eigentümer/Empfänger, SELF=nur eigener Datensatz,
# VIS=Gast-Sichtbarkeit (guest_view_all_features), PAGE=Page-Zugriffsregel, WSA|PA = Workspace-Admin ODER Projekt-Admin (ohne Mitgliedschaft)
DROP = "entfällt"
T = {}  # (class, action, http) -> (target, deviation-id)
def t(cls, action, http, target, dev="", area=None):
    T[(area, cls, action, http)] = (target, dev)
for cls in ["CycleViewSet","IssueViewSet","IssueCommentViewSet","ModuleViewSet","ProjectViewSet","IssueViewViewSet","WorkspaceViewViewSet","WorkSpaceViewSet"]:
    t(cls,"update","PUT",DROP,"SEC-01")
for a,h in [("retrieve","GET"),("update","PUT"),("partial_update","PATCH")]:
    t("CycleIssueViewSet",a,h,DROP,"SEC-02"); t("ModuleIssueViewSet",a,h,DROP,"SEC-02")
t("ProjectViewSet","partial_update","PATCH","WSA|PA")
t("ProjectViewSet","destroy","DELETE","WSA|PA")
t("CycleFavoriteViewSet","list","GET","PRJ(A,M,G)+OWN")
t("IssueViewFavoriteViewSet","list","GET","PRJ(A,M,G)+OWN")
t("ProjectFavoritesViewSet","list","GET",DROP,"SEC-11")
t("ProjectFavoritesViewSet","create","POST","WS(A,M,G)+PRJ-MEMBER")
t("ProjectFavoritesViewSet","destroy","DELETE","WS(A,M,G)+OWN")
t("IntakeViewSet","create","POST","PRJ(A)+O","SEC-03")
t("IntakeViewSet","partial_update","PATCH","PRJ(A)+O","SEC-03")
t("IntakeViewSet","retrieve","GET","PRJ(A,M)+O","SEC-03")
t("IssueCommentViewSet","retrieve","GET","PRJ(A,M,G)+VIS","SEC-04")
t("IssueReactionViewSet","list","GET","PRJ(A,M,G)+VIS","SEC-04")
t("CommentReactionViewSet","list","GET","PRJ(A,M,G)+VIS","SEC-04")
t("IssueDetailIdentifierEndpoint","get","GET","PRJ(A,M,G)+VIS")
t("NotificationViewSet","retrieve","GET","WS(A,M,G)+OWN")
t("NotificationViewSet","destroy","DELETE","WS(A,M,G)+OWN")
for a,h in [("list","GET"),("retrieve","GET"),("destroy","DELETE")]:
    t("ProjectInvitationsViewset",a,h,"PRJ(A)+O","SEC-05")
t("UserProjectInvitationsViewset","list","GET","AUTH+SELF","SEC-06")
t("ProjectUserViewsEndpoint","post","POST","PRJ(A,M,G)+SELF")
t("ProjectMemberUserEndpoint","get","GET","PRJ(A,M,G)+SELF")
t("GlobalSearchEndpoint","get","GET","WS(A,M,G)+VIS")
t("IssueSearchEndpoint","get","GET","PRJ(A,M,G)+VIS", area="app")
t("StateViewSet","retrieve","GET","PRJ(A,M,G)")
for c in ["UserActivityGraphEndpoint","UserIssueCompletedGraphEndpoint","UserWorkspaceDashboardEndpoint"]:
    t(c,"get","GET","WS(A,M,G)+SELF")
t("IssueViewViewSet","create","POST","PRJ(A,M)+O","SEC-07")
t("WorkspaceViewViewSet","create","POST","WS(A,M)","SEC-07")
t("WorkspaceViewViewSet","retrieve","GET","WS(A,M,G)+VIS","SEC-07")
t("WorkSpaceViewSet","retrieve","GET","WS(A,M,G)")
t("WorkspaceMemberUserEndpoint","get","GET","WS(A,M,G)+SELF")
t("WorkspaceMemberUserViewsEndpoint","post","POST","WS(A,M,G)+SELF")
t("WorkspaceUserProfileEndpoint","get","GET","WS(A,M,G)")
t("WorkspaceStickyViewSet","retrieve","GET","WS(A,M,G)+OWN")
t("WorkspaceStickyViewSet","list","GET","WS(A,M,G)+OWN")
# v1 harmonisation / security fixes
for h in ["GET","POST"]:
    t("IssueAttachmentListCreateAPIEndpoint",h.lower(),h,"PRJ(A,M,G)+O+VIS" if h=="GET" else "PRJ(A,M,G)+O","SEC-08")
t("IssueAttachmentDetailAPIEndpoint","get","GET","PRJ(A,M,G)+O+VIS","SEC-08")
t("IssueAttachmentDetailAPIEndpoint","patch","PATCH","PRJ(A,M,G)+O","SEC-08")
t("IssueAttachmentDetailAPIEndpoint","delete","DELETE","PRJ(A)+O+C:FileAsset","SEC-08")
t("IssueSearchEndpoint","get","GET","WS(A,M,G)+VIS", area="api")
t("IssueCommentDetailAPIEndpoint","patch","PATCH","PRJ(A)+O+C:IssueComment","SEC-09")
t("IssueCommentDetailAPIEndpoint","delete","DELETE","PRJ(A)+O+C:IssueComment","SEC-09")
t("ProjectSummaryAPIEndpoint","get","GET","PRJ(A,M)+O","SEC-10")
t("ProjectArchiveUnarchiveAPIEndpoint","post","POST","PRJ(A,M)+O","HARM-05")
t("ProjectArchiveUnarchiveAPIEndpoint","delete","DELETE","PRJ(A,M)+O","HARM-05")
t("ProjectDetailAPIEndpoint","delete","DELETE","WSA|PA","HARM-06")
t("ProjectDetailAPIEndpoint","patch","PATCH","WSA|PA","HARM-06")
t("CycleDetailAPIEndpoint","delete","DELETE","PRJ(A)+O+C:Cycle","SEC-20")
t("ModuleDetailAPIEndpoint","delete","DELETE","PRJ(A)+O+C:Module","SEC-20")
for h,a in [("GET","get")]:
    t("CycleArchiveUnarchiveAPIEndpoint",a,h,"PRJ(A,M)+O","HARM-02")
t("LabelViewSet","list","GET","PRJ(A,M,G)","SEC-21")
t("LabelViewSet","retrieve","GET","PRJ(A,M,G)","SEC-21")
t("IntakeIssueDetailAPIEndpoint","get","GET","PRJ(A,M,G)+O+C:Issue+VIS","HARM-01")
t("StickyViewSet","partial_update","PATCH","WS(A,M,G)+C:Sticky","SEC-13")
t("StickyViewSet","destroy","DELETE","WS(A,M,G)+C:Sticky","SEC-13")
t("StickyViewSet","retrieve","GET","WS(A,M,G)+OWN")
t("StickyViewSet","list","GET","WS(A,M,G)+OWN")
t("IssueDetailAPIEndpoint","delete","DELETE","PRJ(A)+O+C:Issue","SEC-14")
t("IntakeIssueDetailAPIEndpoint","patch","PATCH","PRJ(A)+O+C:Issue","HARM-01")
t("IntakeIssueDetailAPIEndpoint","delete","DELETE","PRJ(A)+O+C:Issue","HARM-01")
t("CycleIssueListCreateAPIEndpoint","get","GET","PRJ(A,M)+O","HARM-02")
t("CycleIssueDetailAPIEndpoint","get","GET","PRJ(A,M)+O","HARM-02")
t("ModuleIssueListCreateAPIEndpoint","get","GET","PRJ(A,M)+O","HARM-02")
t("ModuleIssueDetailAPIEndpoint","get","GET","PRJ(A,M)+O","HARM-02")
t("WorkspaceMemberAPIEndpoint","get","GET","WS(A,M,G)","HARM-03")
t("WorkspaceMemberLiteAPIEndpoint","get","GET","WS(A,M,G)","HARM-03")
for a,h in [("list","GET"),("retrieve","GET"),("create","POST"),("partial_update","PATCH"),("destroy","DELETE")]:
    t("WorkspaceInvitationsViewset",a,h,"WS(A,M)","HARM-04", area="api")
t("WorkspaceDraftIssueViewSet","retrieve","GET","WS(A,M,G)+OWN","SEC-15")
t("WorkspaceDraftIssueViewSet","partial_update","PATCH","WS(A,M,G)+OWN","SEC-15")
t("WorkspaceDraftIssueViewSet","destroy","DELETE","WS(A,M,G)+OWN","SEC-15")
t("WorkspaceDraftIssueViewSet","list","GET","WS(A,M,G)+OWN")
t("DeployBoardViewSet","retrieve","GET","PRJ(A,M,G)","SEC-16")
t("DeployBoardViewSet","partial_update","PATCH","PRJ(A,M)","SEC-16")
t("DeployBoardViewSet","destroy","DELETE","PRJ(A,M)","SEC-16")
t("ProjectMemberPreferenceEndpoint","patch","PATCH","PRJ(A,M,G)+O+SELF","SEC-17")
t("InstanceAdminEndpoint","post","POST",DROP,"ADR-008")
t("InstanceAdminEndpoint","delete","DELETE",DROP,"ADR-008")
for a in ["post"]:
    for c in ["InstanceAdminSignOutEndpoint","InstanceAdminSignInEndpoint","InstanceAdminSignUpEndpoint"]:
        t(c,a,"POST",DROP,"ADR-008")
t("SignUpScreenVisitedEndpoint","post","POST",DROP,"ADR-008")
t("AccountEndpoint","get","GET",DROP,"ADR-008"); t("AccountEndpoint","delete","DELETE",DROP,"ADR-008")
t("UserEndpoint","generate_email_verification_code","POST",DROP,"ADR-008")
t("UserEndpoint","update_email","PATCH",DROP,"ADR-008")
t("IssueCommentPublicViewSet","list","GET","ANON+BOARD")
t("IssueCommentPublicViewSet","retrieve","GET","ANON+BOARD")
t("IntakeIssuePublicViewSet","list","GET","AUTH+BOARD+OWN","SEC-18")
t("IntakeIssuePublicViewSet","retrieve","GET","AUTH+BOARD+OWN","SEC-18")
t("EntityAssetEndpoint","patch","PATCH","AUTH+BOARD+OWN","SEC-19")
t("EntityAssetEndpoint","delete","DELETE","AUTH+BOARD+OWN","SEC-19")
t("AssetRestoreEndpoint","post","POST","AUTH+BOARD+OWN","SEC-19", area="space")  # space variant only (area check below)

def norm(req):
    s = req.replace("PRJ+(", "PRJ(").replace(" ","")
    return s

def derive_target(r):
    for key in ((r["area"], r["class"], r["action"], r["http"]), (None, r["class"], r["action"], r["http"])):
        if key in T: return T[key]
    req = r["req"]
    if r["class"]=="IssueSubscriberViewSet": pass
    # mechanical translation
    if req == "Anon": return ("ANON", "")
    if req == "Auth": return ("AUTH+SELF" if r["key"].startswith("user.") else "AUTH", "")
    if req == "INST": return ("INST", "")
    parts = [p.strip() for p in req.split("∧")]
    last = parts[-1]
    # take most specific (decorator) part
    rules=[]
    m = re.match(r"(WS|PRJ\+?|PAGE)\(([AMG,]+)\)(?: ∨ Creator\((\w+)\))?$", last)
    m2 = re.match(r"Creator\((\w+)\)$", last)
    if m2:
        lvl = "WS" if r["key"].startswith("workspace") else "PRJ"
        return (f"{lvl}(A,M,G)+C:{m2.group(1)}", "")
    if not m: return ("?"+req,"")
    lvl, roles, cm = m.group(1), m.group(2), m.group(3)
    if lvl == "PRJ+": rules.append("O"); lvl="PRJ"
    if lvl == "PAGE": rules.append("PAGE"); lvl="PRJ"
    if cm: rules.append("C:"+cm)
    return (f"{lvl}({roles})" + "".join("+"+x for x in rules), "")

out=[]
for r in rows:
    k = refine(r)
    tgt, dev = derive_target(r)
    out.append({**r, "pkey": k, "target": tgt, "dev": dev})

# visibility rule (guest_view_all_features) applies on read lists of these keys
VIS_KEYS = {"project.work_item.read","project.work_item.read_archived","project.work_item_comment.read","project.work_item_activity.read",
            "project.intake_work_item.read","project.view.read","workspace.view.read","project.page.read","workspace.search.read",
            "workspace.member_profile.read","workspace.member_profile.read_own","workspace.export.create","project.work_item.search","workspace.favorite.read"}
for o in out:
    if o["pkey"] in VIS_KEYS and o["target"] not in (DROP,) and "VIS" not in o["target"] and o["target"].startswith(("PRJ","WS")):
        o["target"] += "+VIS"
for o in out:
    o["target"] = re.sub(r"\+O(?=\+|$)", "", o["target"])
    if o["area"]=="space" and o["target"]=="AUTH": o["target"]="AUTH+BOARD"
json.dump(out, open(sys.argv[2],"w"), indent=1, ensure_ascii=False)

# consistency: role set per key
g = collections.defaultdict(set)
for o in out:
    if o["target"]==DROP: continue
    m = re.match(r"(WS|PRJ|ANON|AUTH|INST|WSA\|PA)(?:\(([AMG,]+)\))?", o["target"])
    g[o["pkey"]].add((m.group(1), m.group(2)))
bad = {k:v for k,v in g.items() if len(v)>1}
print("keys", len(g), "inconsistent", len(bad))
for k,v in sorted(bad.items()):
    print(k, v, [ (o["http"], o["route"][-60:], o["class"], o["target"]) for o in out if o["pkey"]==k])
print("unknown", [o for o in out if o["target"].startswith("?")][:5])
