import {
  useMemo,
  useState,
  type FormEvent,
} from "react";

import { useCreateProject } from "../features/projects/project-mutations";
import { useProjects } from "../features/projects/project-queries";
import { useWorkspace } from "../features/workspaces/use-workspace";
import { ApiError } from "../services/api-client";

function createSlug(value: string): string {
  return value
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "-")
    .replace(/^-+|-+$/g, "");
}

export function ProjectsPage() {
  const {
    currentWorkspace,
    isLoading: isWorkspaceLoading,
    isError: isWorkspaceError,
  } = useWorkspace();

  const {
    data: projects = [],
    isLoading: isProjectsLoading,
    isError: isProjectsError,
  } = useProjects(
    currentWorkspace?.id ?? null,
  );

  const createProjectMutation = useCreateProject();

  const [isCreateFormOpen, setIsCreateFormOpen] =
    useState(false);

  const [name, setName] = useState("");
  const [slug, setSlug] = useState("");
  const [description, setDescription] = useState("");
  const [isSlugEdited, setIsSlugEdited] = useState(false);
  const [formError, setFormError] =
    useState<string | null>(null);

  const normalizedSlug = useMemo(
    () => createSlug(slug),
    [slug],
  );

  function resetForm() {
    setName("");
    setSlug("");
    setDescription("");
    setIsSlugEdited(false);
    setFormError(null);
  }

  function handleNameChange(value: string) {
    setName(value);

    if (!isSlugEdited) {
      setSlug(
        createSlug(value),
      );
    }
  }

  async function handleCreateProject(
    event: FormEvent<HTMLFormElement>,
  ) {
    event.preventDefault();

    if (!currentWorkspace) {
      return;
    }

    const normalizedName = name.trim();

    if (!normalizedName) {
      setFormError("Project name is required.");
      return;
    }

    if (!normalizedSlug) {
      setFormError("Project slug is required.");
      return;
    }

    setFormError(null);

    try {
      await createProjectMutation.mutateAsync({
        workspaceId: currentWorkspace.id,
        project: {
          name: normalizedName,
          slug: normalizedSlug,
          description:
            description.trim() || null,
        },
      });

      resetForm();
      setIsCreateFormOpen(false);
    } catch (error) {
      if (error instanceof ApiError) {
        setFormError(error.message);
      } else {
        setFormError(
          "Unable to create project. Please try again.",
        );
      }
    }
  }

  if (isWorkspaceLoading) {
    return (
      <section className="page-section">
        <p>Loading workspace...</p>
      </section>
    );
  }

  if (isWorkspaceError) {
    return (
      <section className="page-section">
        <p>Unable to load workspace.</p>
      </section>
    );
  }

  if (!currentWorkspace) {
    return (
      <section className="page-section">
        <div className="page-heading">
          <div>
            <p className="page-eyebrow">
              Projects
            </p>

            <h1>Create your first workspace</h1>

            <p>
              Projects belong to a workspace. Create a workspace
              before registering projects and AI agents.
            </p>
          </div>
        </div>
      </section>
    );
  }

  if (isProjectsLoading) {
    return (
      <section className="page-section">
        <p>Loading projects...</p>
      </section>
    );
  }

  if (isProjectsError) {
    return (
      <section className="page-section">
        <p>Unable to load projects.</p>
      </section>
    );
  }

  return (
    <section className="page-section">
      <div className="page-heading">
        <div>
          <p className="page-eyebrow">
            Projects
          </p>

          <h1>{currentWorkspace.name} Projects</h1>

          <p>
            Organize AI agents, deployments, usage, and governance
            within this workspace.
          </p>
        </div>

        <button
          type="button"
          className="topbar-button"
          onClick={() => {
            setFormError(null);
            setIsCreateFormOpen((value) => !value);
          }}
        >
          {isCreateFormOpen
            ? "Cancel"
            : "Create Project"}
        </button>
      </div>

      {isCreateFormOpen ? (
        <form
          className="project-create-form"
          onSubmit={handleCreateProject}
        >
          <label>
            <span>Project name</span>

            <input
              type="text"
              value={name}
              onChange={(event) =>
                handleNameChange(event.target.value)
              }
              maxLength={255}
              disabled={createProjectMutation.isPending}
              required
            />
          </label>

          <label>
            <span>Slug</span>

            <input
              type="text"
              value={slug}
              onChange={(event) => {
                setIsSlugEdited(true);
                setSlug(event.target.value);
              }}
              pattern="[a-z0-9]+(?:-[a-z0-9]+)*"
              maxLength={100}
              disabled={createProjectMutation.isPending}
              required
            />
          </label>

          <label>
            <span>Description</span>

            <textarea
              value={description}
              onChange={(event) =>
                setDescription(event.target.value)
              }
              maxLength={1000}
              disabled={createProjectMutation.isPending}
            />
          </label>

          {formError ? (
            <p role="alert">
              {formError}
            </p>
          ) : null}

          <button
            type="submit"
            className="topbar-button"
            disabled={createProjectMutation.isPending}
          >
            {createProjectMutation.isPending
              ? "Creating..."
              : "Create Project"}
          </button>
        </form>
      ) : null}

      {projects.length === 0 ? (
        <div className="empty-state">
          <h2>No projects yet</h2>

          <p>
            Create a project to start registering and managing AI agents.
          </p>
        </div>
      ) : (
        <div className="project-grid">
          {projects.map((project) => (
            <article
              key={project.id}
              className="project-card"
            >
              <div className="project-card-header">
                <div>
                  <p className="project-slug">
                    {project.slug}
                  </p>

                  <h2>{project.name}</h2>
                </div>

                <span className="project-status">
                  {project.is_active
                    ? "Active"
                    : "Inactive"}
                </span>
              </div>

              <p className="project-description">
                {project.description
                  ?? "No description provided."}
              </p>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}
